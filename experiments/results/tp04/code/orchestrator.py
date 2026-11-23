"""Orchestration locale bornée. Les contrôles sont communs aux quatre stratégies."""
import hashlib
import json
import multiprocessing as mp
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT = (ROOT / 'configs/prompts/report_v2.txt').read_text()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def utc():
    return datetime.now(timezone.utc).isoformat()

@dataclass(frozen=True)
class Policy:
    max_calls: int = 2
    max_tokens_total: int = 4600
    call_timeout_s: float = 20
    request_timeout_s: float = 45
    max_input_tokens: int = 2048
    retries: int = 0


def _serve(connection, role):
    from local_llm import LocalLLM
    import torch
    torch.set_num_threads(4)
    torch.manual_seed(42)
    try:
        model = LocalLLM(role)
        model.generate({'amount':20,'score':0.1,'needs_review':False}, system_prompt=PROMPT)
        connection.send({'ready':True,'load_seconds':model.load_seconds})
        while True:
            request = connection.recv()
            if request is None:
                return
            try:
                if request.get('custom_prompt'):
                    messages = [{'role':'user','content':request['custom_prompt']}]
                    inputs=model.tokenizer.apply_chat_template(messages,add_generation_prompt=True,tokenize=True,return_tensors='pt',return_dict=True)
                    n=inputs['input_ids'].shape[1]
                    if n > request['max_input_tokens']:
                        raise ValueError('input_token_limit')
                    start=time.perf_counter()
                    with torch.inference_mode():
                        output=model.model.generate(**inputs,max_new_tokens=100,do_sample=False,pad_token_id=model.tokenizer.eos_token_id)
                    result={'text':model.tokenizer.decode(output[0,n:],skip_special_tokens=True),'seconds':time.perf_counter()-start,'input_tokens':n,'output_tokens':output.shape[1]-n,'model_id':model.config['model_id'],'revision':model.config['revision']}
                else:
                    from local_llm import make_prompt
                    messages=[{'role':'system','content':PROMPT},{'role':'user','content':make_prompt(request['facts'])}]
                    tokens=model.tokenizer.apply_chat_template(messages,add_generation_prompt=True,tokenize=True)
                    if len(tokens)>request['max_input_tokens']:
                        raise ValueError('input_token_limit')
                    result=model.generate(request['facts'],system_prompt=PROMPT)
                connection.send({'result':result})
            except Exception as error:
                connection.send({'error':type(error).__name__,'reason':str(error)[:80]})
    except (Exception, EOFError) as error:
        try: connection.send({'error':type(error).__name__})
        except (OSError,EOFError): pass
    finally:
        connection.close()

class ModelWorker:
    """Processus interruptible, délai réellement borné et non un thread abandonné."""
    def __init__(self, role):
        self.role=role
        self.process=None
        self.connection=None

    def start(self):
        self.close()
        parent, child=mp.get_context('spawn').Pipe()
        self.connection=parent
        self.process=mp.get_context('spawn').Process(target=_serve,args=(child,self.role),daemon=True)
        self.process.start()
        child.close()
        if not parent.poll(120):
            self.close()
            raise TimeoutError('model_load_timeout')
        reply=parent.recv()
        if not reply.get('ready'):
            self.close()
            raise RuntimeError('model_load_failed')
        return reply

    def alive(self):
        return bool(self.process and self.process.is_alive())

    def call(self, facts, timeout_s, max_input_tokens, custom_prompt=None):
        if not self.alive():
            raise RuntimeError('backend_unavailable')
        self.connection.send({'facts':facts,'max_input_tokens':max_input_tokens,'custom_prompt':custom_prompt})
        if not self.connection.poll(timeout_s):
            self.close()
            raise TimeoutError('inference_timeout')
        try: reply=self.connection.recv()
        except (EOFError,OSError) as error: raise RuntimeError('backend_disconnected') from error
        if 'error' in reply:
            raise RuntimeError(reply['error']+':'+reply.get('reason',''))
        return reply['result']

    def close(self):
        if self.process:
            if self.process.is_alive():
                self.process.terminate()
            self.process.join(timeout=2)
            if self.process.is_alive():
                self.process.kill()
                self.process.join(timeout=2)
        if self.connection:
            self.connection.close()
        self.process=None
        self.connection=None


def expected_report(facts):
    return {'amount':facts.get('amount'),'score':facts.get('score'),'country':facts.get('country','unknown'),
            'action':'review' if facts.get('needs_review') and facts.get('amount') is not None else 'abstain'}


def strict_check(text, expected):
    """JSON pur, champs/types stricts, pas d'égalité True == 1 ni NaN."""
    try:
        def reject(x): raise ValueError(x)
        def unique(pairs):
            result={}
            for key,value in pairs:
                if key in result: raise ValueError('duplicate_key')
                result[key]=value
            return result
        report=json.loads(text,parse_constant=reject,object_pairs_hook=unique)
        if not isinstance(report,dict) or set(report)!=set(expected): return False
        for key in ['amount','score']:
            v=report[key]
            if v is not None and (isinstance(v,bool) or not isinstance(v,(int,float))): return False
        if not isinstance(report['country'],str) or not isinstance(report['action'],str): return False
        return report==expected
    except (ValueError,TypeError,KeyError):
        return False


def guard(case):
    """Métadonnées de provenance structurées de la fixture, jamais interprétation d'une note."""
    facts=case['facts']
    if case.get('sensitive'):
        return {'amount':None,'score':None,'country':'unknown','action':'abstain'},'sensitive_or_out_of_scope'
    if not case.get('source_available',True):
        return {'amount':None,'score':None,'country':'unknown','action':'abstain'},'source_absent'
    if case.get('source_conflict',False):
        return {'amount':None,'score':None,'country':'unknown','action':'abstain'},'source_conflict'
    return None,None


class Orchestrator:
    def __init__(self, workers, policy=None):
        self.workers=workers
        self.policy=policy or Policy()

    def run(self, case, strategy):
        if strategy not in {'mono_a','mono_b','routing','cascade'}: raise ValueError('unknown_strategy')
        start=time.perf_counter()
        traces=[]
        trace_id=str(uuid.uuid4())
        case_hash=digest(case)
        expected=case['expected']
        guarded,reason=guard(case)
        base={'trace_id':trace_id,'case_id':case['id'],'case_sha256':case_hash,'category':case['category'],
              'strategy':strategy,'timestamp_utc':utc(),'policy':asdict(self.policy),'prompt_sha256':hashlib.sha256(PROMPT.encode()).hexdigest()}
        if guarded is not None:
            return {**base,'status':'guarded','reason':reason,'report':guarded,'contract_pass':guarded==expected,
                    'seconds':time.perf_counter()-start,'calls':0,'input_tokens':0,'output_tokens':0,'traces':[],'ttft_s':None}
        route='writer' if strategy in {'mono_a','cascade'} else 'verifier'
        if strategy=='routing':
            route='verifier' if case.get('complex',False) or 'untrusted_note' in case['facts'] else 'writer'
        result=None
        total_tokens=0
        status='failed'
        reason='invalid_output'
        max_attempts=2 if strategy=='cascade' else 1
        for attempt in range(max_attempts):
            # Réserve pour le pire cas : contexte max + 100 nouveaux tokens.
            if len(traces)>=self.policy.max_calls or total_tokens+self.policy.max_input_tokens+100>self.policy.max_tokens_total:
                reason='budget_stop'
                break
            remaining=self.policy.request_timeout_s-(time.perf_counter()-start)
            if remaining<=2:
                reason='request_timeout'
                break
            call_start=time.perf_counter()
            config=json.loads((ROOT/'configs/llm_models.json').read_text())[route]
            trace={'role':route,'provider':'local_transformers','model_id':config['model_id'],'revision':config['revision'],
                   'started_utc':utc(),'attempt':attempt+1,'route_reason':strategy,'status':'error','input_tokens':None,'output_tokens':None}
            try:
                result=self.workers[route].call(case['facts'],min(self.policy.call_timeout_s,remaining-2),self.policy.max_input_tokens)
                trace.update({k:result[k] for k in ['input_tokens','output_tokens','model_id','revision']})
                total_tokens+=result['input_tokens']+result['output_tokens']
                valid=strict_check(result['text'],expected)
                trace.update(status='accepted' if valid else 'invalid_output',output=result['text'])
                if valid:
                    status='accepted'
                    reason='validated_contract'
            except (RuntimeError,TimeoutError,OSError,EOFError) as error:
                # Réserver le coût maximal d'un appel interrompu dont l'usage exact est inconnu.
                total_tokens+=self.policy.max_input_tokens+100
                reason='timeout' if isinstance(error,TimeoutError) else 'backend_error'
                trace.update(error=type(error).__name__,status=reason)
            trace['seconds']=time.perf_counter()-call_start
            traces.append(trace)
            if status=='accepted': break
            route='verifier'
        report=json.loads(result['text']) if status=='accepted' else {**expected_report(case['facts']),'action':'abstain'}
        return {**base,'status':status,'reason':reason,'report':report,'contract_pass':status=='accepted',
                'seconds':time.perf_counter()-start,'calls':len(traces),
                'input_tokens':sum(t['input_tokens'] or 0 for t in traces),'output_tokens':sum(t['output_tokens'] or 0 for t in traces),
                'usage_complete':all(t['input_tokens'] is not None for t in traces),'traces':traces,'ttft_s':None}
