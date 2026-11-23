import argparse,json,urllib.request,urllib.error
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--base-url',default='http://127.0.0.1:8767')
args=parser.parse_args()
base=args.base_url.rstrip('/')
results=[]
def call(path,body=None):
 data=None if body is None else json.dumps(body).encode()
 request=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(request,timeout=180) as r:return r.status,json.load(r)
 except urllib.error.HTTPError as e:return e.code,json.load(e)
def check(name,condition):
 results.append({'test':name,'passed':bool(condition)})
 assert condition,name
code,status=call('/api/status');check('statut et test final',code==200 and status['test_evaluated'])
code,cases=call('/api/cases');check('dossiers sans label cible',code==200 and len(cases)==10 and all('Class' not in c for c in cases))
code,pred=call('/api/predict',cases[0]);check('score et persistance',code==200 and 0<=pred['score']<=1 and pred['id'])
for mode in ['template','mono_a','mono_b','routing','cascade']:
 code,result=call('/api/analyze',{'prediction_id':pred['id'],'mode':mode})
 check('rapport '+mode,code==200 and bool(result['text']) and 'contract_valid' in result)
code,result=call('/api/decision',{'prediction_id':pred['id'],'action':'approfondir'});check('avis humain',code==200)
code,result=call('/api/generate',{'count':4,'seed':42});check('generation reelle',code==200 and result['accepted']+result['rejected']==4)
code,hist=call('/api/history');check('journal SQLite',code==200 and any(r['kind']=='human_decision' for r in hist))
code,result=call('/api/predict',{'features':[1,2]});check('refus mauvais schema',code==422)
code,result=call('/api/predict',{'features':[0]*28+[-1]});check('refus montant negatif',code==422)
code,result=call('/api/analyze',{'prediction_id':'absent','mode':'template'});check('refus dossier absent',code==404)
code,result=call('/api/decision',{'prediction_id':pred['id'],'action':'bloquer_compte'});check('refus action non permise',code==422)
code,result=call('/api/generate',{'count':999,'seed':42});check('limite generation',code==422)
(Path(__file__).resolve().parents[1]/'experiments/application_checks_latest.json').write_text(json.dumps({'origin':'verification automatique locale avec donnees validation','checks':results},indent=2))
print(json.dumps(results,indent=2))
