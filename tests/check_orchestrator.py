"""Tests d'orchestration simulés, distincts de la qualité des vrais LLM."""
import json
import sys
from dataclasses import replace
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from orchestrator import Orchestrator, Policy, expected_report, strict_check, ROOT

class Fake:
    def __init__(self, mode='valid'): self.mode=mode;self.calls=0
    def call(self,facts,timeout_s,max_input_tokens):
        self.calls+=1
        if self.mode=='timeout': raise TimeoutError('controlled')
        if self.mode=='down': raise RuntimeError('unavailable')
        return {'text':json.dumps(expected_report(facts)) if self.mode=='valid' else 'invalid','input_tokens':100,'output_tokens':30,'model_id':'test-double','revision':'test-only'}

cases=[json.loads(l) for l in (ROOT/'experiments/test_cases_tp04.jsonl').read_text().splitlines()]
checks=[]
def check(name,value):
    checks.append({'test':name,'passed':bool(value),'proof':'simulated_orchestration_not_llm_quality'})
    assert value,name

def run(a='valid',b='valid',strategy='cascade',policy=None,case=cases[1]):
    return Orchestrator({'writer':Fake(a),'verifier':Fake(b)},policy).run(case,strategy)
r=run(a='invalid');check('invalid A repaired by B',r['contract_pass'] and r['calls']==2)
r=run(a='invalid',b='down');check('B unavailable yields abstention and failure',not r['contract_pass'] and r['report']['action']=='abstain' and r['calls']==2)
r=run(a='timeout');check('timeout A bounded then B',r['contract_pass'] and r['calls']==2 and r['traces'][0]['status']=='timeout')
r=run(a='invalid',policy=replace(Policy(),max_calls=1));check('max calls enforced',not r['contract_pass'] and r['calls']==1 and r['reason']=='budget_stop')
r=run(policy=replace(Policy(),max_tokens_total=100));check('token budget stops before model',r['calls']==0 and r['reason']=='budget_stop')
r=run(policy=replace(Policy(),request_timeout_s=0));check('deadline stops before model',r['calls']==0 and r['reason']=='request_timeout')
r=run();check('cascade valid A skips B',r['calls']==1 and r['contract_pass'])
for c in cases[6:8]+cases[9:]:
 r=run(case=c);check('guard '+c['id'],r['calls']==0 and r['contract_pass'])
r=run(strategy='routing',case=cases[8]);check('injection routed B and not instructions',r['traces'][0]['role']=='verifier' and r['report']['action']=='review')
e=expected_report(cases[1]['facts']);check('reject boolean numeric',not strict_check(json.dumps({**e,'amount':True}),e))
check('reject duplicate fields',not strict_check('{"amount":1200,"amount":1200,"score":0.95,"country":"unknown","action":"review"}',e))
check('reject markdown',not strict_check('```json\n'+json.dumps(e)+'\n```',e))
(ROOT/'experiments/results/tp04_robustness.json').write_text(json.dumps(checks,indent=2))
print(f'{len(checks)} tests réussis')
