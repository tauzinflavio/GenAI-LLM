"""Bornes HTTP, journal minimal et réactivation du service. Aucune mesure de qualité humaine."""
import argparse,json,sys,sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from service_checks import ROOT,call
p=argparse.ArgumentParser();p.add_argument('--base-url',default='http://127.0.0.1:8784');a=p.parse_args();base=a.base_url
checks=[]
def check(name,condition):
 checks.append({'test':name,'passed':bool(condition)});assert condition,name
code,_,_=call(base,'/healthz');check('API vivante',code==200)
code,r,_=call(base,'/readyz');check('deux workers prêts',code==200 and all(m['alive'] for m in r['models']))
code,cases,_=call(base,'/api/cases');case={**cases[-1],'reference':'PII_SENTINEL_TEST'}
code,pred,_=call(base,'/api/predict',case);check('transaction autorisée',code==200)
with sqlite3.connect(ROOT/'data/local_app.sqlite') as db:
 payload=db.execute('SELECT payload FROM events WHERE id=?',(pred['id'],)).fetchone()[0]
check('référence libre absente du stockage', 'PII_SENTINEL_TEST' not in payload and 'reference_sha256' in payload)
code,result,_=call(base,'/v1/generate',{'amount':20,'score':.1,'needs_review':False,'strategy':'mono_b'})
check('vraie inférence conforme',code==200 and result['calls']>0 and result['contract_pass'])
with sqlite3.connect(ROOT/'data/local_app.sqlite') as db:
 payload=json.loads(db.execute("SELECT payload FROM events WHERE kind='service_generation' ORDER BY rowid DESC LIMIT 1").fetchone()[0])
check('journal du service minimal',set(payload)=={'trace_id','strategy','status','calls','seconds','contract_pass'})
for name,body in [('montant négatif',{'amount':-1}),('score hors bornes',{'score':2}),('stratégie inconnue',{'strategy':'cloud'}),('texte libre non autorisé',{'prompt':'secret'})]:
 code,_,_=call(base,'/v1/generate',body);check('refus '+name,code==422)
code,_,_=call(base,'/api/recover',{});check('réactivation explicite acceptée',code==202)
(ROOT/'experiments/results/service_safety.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print(len(checks),'tests réussis')
