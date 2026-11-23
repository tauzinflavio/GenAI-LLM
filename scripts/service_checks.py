"""TP08 : smoke et charge HTTP réels, prompts fictifs, sans entrée libre dans les preuves."""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import platform
import time
import urllib.error
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import psutil

ROOT=Path(__file__).resolve().parents[1]
FACTS={'amount':20,'score':0.1,'needs_review':False,'strategy':'mono_b'}

def call(base,path,body=None):
    request=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
    start=time.perf_counter()
    try:
        with urllib.request.urlopen(request,timeout=60) as response:
            return response.status,json.load(response),time.perf_counter()-start
    except urllib.error.HTTPError as error:
        return error.code,json.load(error),time.perf_counter()-start

def smoke(base,destination):
    h,health,_=call(base,'/healthz');r,ready,_=call(base,'/readyz')
    code,result,seconds=call(base,'/v1/generate',FACTS)
    evidence={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'health_http':h,'ready_http':r,'inference_http':code,
        'trace_id':result.get('trace_id'),'status':result.get('status'),'contract_pass':result.get('contract_pass',False),
        'seconds':seconds,'models':[{k:m[k] for k in ['role','model_id','revision','alive']} for m in ready.get('models',[])],
        'real_inference':bool(result.get('calls',0)>0),'prompt_recorded':False,'output_recorded':False,
        'calls':result.get('calls',0),'scope':'local CPU, fixed fictional request; HTTP success distinct from contract quality'}
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(evidence,indent=2))
    print(json.dumps(evidence,indent=2))
    return evidence

def load(base,concurrency,n):
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    path=out/f'load_c{concurrency}.json'
    if path.exists():raise SystemExit('Preuve existante : choisir une autre exécution/dossier.')
    protocol={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'hypothesis':'À requêtes identiques, concurrence 3 améliore le débit des contrats réussis sans doubler le p95 ni augmenter les erreurs par rapport à concurrence 1.',
      'concurrency':concurrency,'requests':n,'request_sha256':hashlib.sha256(json.dumps(FACTS,sort_keys=True).encode()).hexdigest(),
      'platform':platform.platform(),'cpu_count':psutil.cpu_count(),'memory_total_bytes':psutil.virtual_memory().total,
      'model':'Qwen/Qwen2.5-0.5B-Instruct','max_new_tokens':100,'retries':0,'load_warmup_excluded':True,
      'energy':'ND','note':'petit N, p95 descriptif ; admission limitée à une inférence, 429 attendu sous contention'}
    path.with_name(path.stem+'_protocol.json').write_text(json.dumps(protocol,indent=2))
    def task(i):
        code,result,seconds=call(base,'/v1/generate',FACTS)
        return {'request_id':i,'http_status':code,'seconds':seconds,'contract_pass':bool(result.get('contract_pass',False)),
                'trace_id':result.get('trace_id',''),'real_calls':result.get('calls',0)}
    start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool: rows=list(pool.map(task,range(n)))
    elapsed=time.perf_counter()-start
    summary={**protocol,'wall_seconds':elapsed,'http_200':sum(r['http_status']==200 for r in rows),'http_429':sum(r['http_status']==429 for r in rows),
        'other_http_errors':sum(r['http_status'] not in [200,429] for r in rows),'contracts_passed':sum(r['contract_pass'] for r in rows),
        'latency_mean':float(np.mean([r['seconds'] for r in rows])),'latency_p95':float(np.quantile([r['seconds'] for r in rows],.95)),
        'throughput_all_attempts_s':n/elapsed,'throughput_contracts_s':sum(r['contract_pass'] for r in rows)/elapsed,
        'accepted_latency_p95':float(np.quantile([r['seconds'] for r in rows if r['http_status']==200],.95)) if any(r['http_status']==200 for r in rows) else None}
    path.write_text(json.dumps(summary,indent=2))
    with path.with_suffix('.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['smoke','load'])
    parser.add_argument('--base-url',default='http://127.0.0.1:8780')
    parser.add_argument('--concurrency',type=int,choices=[1,3],default=1)
    parser.add_argument('--requests',type=int,default=12)
    parser.add_argument('--output',default='evidence/smoke.json')
    args=parser.parse_args()
    if args.requests<1 or args.requests>24:raise SystemExit('1 à 24 requêtes autorisées pour le TP local')
    if args.command=='smoke':smoke(args.base_url,ROOT/args.output)
    else:load(args.base_url,args.concurrency,args.requests)
