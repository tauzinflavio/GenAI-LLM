"""Comparer les quatre stratégies, sans écraser une expérience existante."""
import argparse
import json
import platform
from dataclasses import asdict
from pathlib import Path
import numpy as np
import pandas as pd
from orchestrator import ROOT, ModelWorker, Orchestrator, Policy, digest, utc

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='experiments/results/tp04')
    args=parser.parse_args()
    out=ROOT/args.output
    if (out/'protocol.json').exists(): raise SystemExit('Utiliser un nouveau dossier pour une nouvelle exécution.')
    cases=[json.loads(line) for line in (ROOT/'experiments/test_cases_tp04.jsonl').read_text().splitlines()]
    out.mkdir(parents=True,exist_ok=True)
    policy=Policy()
    protocol={'frozen_at_utc':utc(),'workload_sha256':digest(cases),'cases':len(cases),'policy':asdict(policy),
        'hypothesis':'La cascade augmente la conformité par rapport à A seul sans dépasser deux appels ; le routing utilise moins d’appels que la cascade.',
        'selection':'max conformité ; puis moins d’appels ; puis p95 ; aucun déploiement bancaire autonome',
        'workload_design':'construit après les expériences V1/V2 ; exploratoire ; aucune généralisation statistique',
        'orchestrator_sha256':__import__('hashlib').sha256((ROOT/'src/orchestrator.py').read_bytes()).hexdigest(),'benchmark_sha256':__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),'model_config_sha256':digest(json.loads((ROOT/'configs/llm_models.json').read_text())),'independent_strategy_backend_reset':True,'hardware':platform.platform(),'machine':platform.machine(),'seed':42,'load_and_warmup_excluded':True,
        'quality':'contrat factuel automatique ; qualité métier et jugement humain non mesurés','energy':'ND','ttft':'ND, sortie non streamée'}
    (out/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2))
    workers={role:ModelWorker(role) for role in ['writer','verifier']}
    try:
        for worker in workers.values(): worker.start()
        runner=Orchestrator(workers,policy)
        records=[]
        # Ordre des stratégies tournant par cas pour limiter un biais de chauffe constant.
        arms=['mono_a','mono_b','routing','cascade']
        for i,case in enumerate(cases):
            for strategy in arms[i%4:]+arms[:i%4]:
                recovery_start=__import__('time').perf_counter()
                recovered_roles=[]
                for role,worker in workers.items():
                    if not worker.alive():
                        worker.start()
                        recovered_roles.append(role)
                recovery_seconds=__import__('time').perf_counter()-recovery_start
                record=runner.run(case,strategy)
                record['pre_run_recovered_roles']=recovered_roles
                record['pre_run_recovery_seconds_excluded']=recovery_seconds if recovered_roles else 0
                records.append(record)
                with (out/'traces.jsonl').open('a') as stream: stream.write(json.dumps(record,ensure_ascii=False)+'\n')
                print(case['id'],strategy,record['status'],record['contract_pass'],flush=True)
        frame=pd.DataFrame([{k:r[k] for k in ['case_id','category','strategy','status','contract_pass','seconds','calls','input_tokens','output_tokens']} for r in records])
        frame.to_csv(out/'metrics.csv',index=False)
        summaries=[]
        for strategy,group in frame.groupby('strategy'):
            llm=group[group.calls>0]
            summaries.append({'strategy':strategy,'cases':len(group),'passes':int(group.contract_pass.sum()),'pass_rate':float(group.contract_pass.mean()),
                'model_cases':len(llm),'model_passes':int(llm.contract_pass.sum()),'guard_cases':int((group.calls==0).sum()),
                'latency_p50':float(group.seconds.median()),'latency_p95':float(np.quantile(group.seconds,.95)),
                'total_seconds':float(group.seconds.sum()),'calls':int(group.calls.sum()),'input_tokens':int(group.input_tokens.sum()),
                'output_tokens':int(group.output_tokens.sum()),'api_cost_eur':0.0,'energy_kwh':None,'co2e_kg':None})
        pd.DataFrame(summaries).to_csv(out/'summary.csv',index=False)
        frame.groupby(['strategy','category']).agg(cases=('contract_pass','size'),passes=('contract_pass','sum'),calls=('calls','sum')).reset_index().to_csv(out/'by_category.csv',index=False)
        frame[['case_id','strategy','status']].assign(human_fidelity='',human_safety='',comment='').to_csv(out/'human_review.csv',index=False)
    finally:
        for worker in workers.values(): worker.close()

if __name__=='__main__': main()
