"""Mini-lab distinct : 4 extractions, 4 raisonnements, 4 synthèses. Grille gelée avant appel."""
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from orchestrator import ROOT,ModelWorker,digest,utc

CASES=[
 {'id':'E1','category':'extraction','task':'Extract the numeric amount from: transaction TX01, amount 125.5, score 0.8.','expected':{'amount':125.5}},
 {'id':'E2','category':'extraction','task':'Extract country from: country FR, amount 70, date 2026-01-02.','expected':{'country':'FR'}},
 {'id':'E3','category':'extraction','task':'Extract transaction_id from: transaction_id TX03, amount 0.','expected':{'transaction_id':'TX03'}},
 {'id':'E4','category':'extraction','task':'Extract score from: transaction TX04, score 0.91, amount 35.','expected':{'score':.91}},
 {'id':'R1','category':'reasoning','task':'Four alerts require 3 minutes each. Compute total minutes.','expected':{'minutes':12}},
 {'id':'R2','category':'reasoning','task':'Annual benefit is 120 euros. Total first-year cost is 100 euros. ROI percent = (benefit-cost)/cost*100. Compute ROI.','expected':{'roi_percent':20}},
 {'id':'R3','category':'reasoning','task':'Rule: review iff score >= 0.8 and amount is known; otherwise abstain. Score=0.9, amount=null. What is the action?','expected':{'action':'abstain'}},
 {'id':'R4','category':'reasoning','task':'A source says amount=100. Another equally authoritative source says amount=200. No tie-break is available. Choose abstain or review.','expected':{'action':'abstain'}},
 {'id':'S1','category':'synthesis','task':'Summarize in one short English sentence: The score is high. The customer identity is unknown. A human must review before any decision. Do not conclude fraud.','required':['score','unknown','human'],'forbidden':['confirmed fraud']},
 {'id':'S2','category':'synthesis','task':'Summarize in one short English sentence: A generates a report. B checks it. Two calls increase latency. A second model does not guarantee accuracy.','required':['latency','accuracy'],'forbidden':['guarantees accuracy']},
 {'id':'S3','category':'synthesis','task':'Summarize in one short English sentence: Inference time was measured. Power was assumed. The energy figure is an estimate, not a direct measurement.','required':['power','estimate'],'forbidden':['energy was measured']},
 {'id':'S4','category':'synthesis','task':'Summarize in one short English sentence: Diffusion AP is slightly higher. The uncertainty interval contains zero. Superiority has not been demonstrated.','required':['zero','superiority'],'forbidden':['superiority is demonstrated']}
]

def prompt(c):
    if c['category']=='synthesis':return c['task']+' Return only the sentence, no other text.'
    keys=', '.join(c['expected'])
    return c['task']+' Return only one JSON object with this exact key: '+keys+'. No explanation.'

def assess(c,text):
    if c['category']=='synthesis':
        normalized=text.strip().lower()
        return all(k in normalized for k in c['required']) and not any(k in normalized for k in c['forbidden'])
    try:return json.loads(text)==c['expected']
    except (ValueError,TypeError):return False

def main():
    out=ROOT/'experiments/m01';out.mkdir(exist_ok=True)
    if (out/'protocol.json').exists():raise SystemExit('Expérience existante à préserver.')
    (out/'cases.json').write_text(json.dumps(CASES,indent=2))
    (out/'protocol.json').write_text(json.dumps({'frozen_utc':utc(),'case_sha256':digest(CASES),'temperature':'greedy','max_new_tokens':100,
        'selection_threshold':'>= 75% overall and >= 50% in each category, no unsupported bank action; otherwise neither',
        'score':'exact JSON for extraction/reasoning; lexical coverage proxy for synthesis, not human semantic evaluation',
        'limits':['12 constructed cases','lexical synthesis metric can miss paraphrases and hallucinations','no independent human grading'],
        'questions':'Would a router by category reduce failures without adding a second call?'},indent=2))
    records=[]
    for role in ['writer','verifier']:
        worker=ModelWorker(role)
        try:
            worker.start()
            for c in CASES:
                start=time.perf_counter()
                try:
                    result=worker.call({},25,2048,custom_prompt=prompt(c));ok=assess(c,result['text'])
                    r={'case_id':c['id'],'category':c['category'],'role':role,**result,'auto_rubric_pass':ok,'wall_seconds':time.perf_counter()-start}
                except (RuntimeError,TimeoutError) as error:
                    r={'case_id':c['id'],'category':c['category'],'role':role,'error':type(error).__name__,'auto_rubric_pass':False,'seconds':time.perf_counter()-start,'input_tokens':None,'output_tokens':None}
                records.append(r)
                (out/'responses.json').write_text(json.dumps(records,indent=2))
                print(role,c['id'],r['auto_rubric_pass'],flush=True)
        finally:worker.close()
    frame=pd.DataFrame(records)
    summary=[]
    for role,g in frame.groupby('role'):
        cats={cat:float(cg.auto_rubric_pass.mean()) for cat,cg in g.groupby('category')}
        summary.append({'role':role,'cases':len(g),'passes':int(g.auto_rubric_pass.sum()),'rate':float(g.auto_rubric_pass.mean()),
          'latency_p50':float(g.seconds.median()),'latency_p95':float(np.quantile(g.seconds,.95)),
          'input_tokens':int(g.input_tokens.sum()),'output_tokens':int(g.output_tokens.sum()),**cats,
          'eligible_auto_only':float(g.auto_rubric_pass.mean())>=.75 and min(cats.values())>=.5})
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False)
    frame[['case_id','role','category']].assign(human_score='',comment='').to_csv(out/'human_review.csv',index=False)

if __name__=='__main__':main()
