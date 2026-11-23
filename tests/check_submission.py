"""Contrôles du rendu TP : notebooks réels, coûts cohérents, ressources bornées et pas de faux humain."""
import csv,hashlib,json,sys,tempfile,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from import_human_reviews import validate
checks=[]
def check(name,condition):
 checks.append(dict(test=name,passed=bool(condition)));assert condition,name
for tp,figs in [('TP01',4),('TP02',1)]:
 p=ROOT/'notebooks'/f'{tp}_FraudLab.ipynb';nb=json.loads(p.read_text());cells=[c for c in nb['cells'] if c['cell_type']=='code'];e=json.loads((ROOT/'experiments'/tp.lower()/'execution.json').read_text())
 check(tp+' toutes cellules réellement exécutées',all(c['execution_count'] and c['outputs'] for c in cells) and e['code_cells_executed']==len(cells))
 check(tp+' figures et sorties conservées',len(e['figures'])==figs and all((ROOT/f).exists() for f in e['figures']))
 check(tp+' aucune erreur',not any(o['output_type']=='error' for c in cells for o in c['outputs']))
 check(tp+' empreinte preuve exacte',e['sha256']==hashlib.sha256(p.read_bytes()).hexdigest())
f=json.loads((ROOT/'experiments/results/financial_checks.json').read_text());check('ventilation et ROI cohérents',f['checks_passed'] and abs(f['roi_central']-13.043478260869565)<1e-10)
review=json.loads((ROOT/'experiments/results/review_inventory.json').read_text());check('158 sorties, aucune annotation inventée',review['records']==158 and review['human_reviews_generated']==0)
for rel,fields in [('experiments/llm_v1/human_review.csv',['fidelite_humaine']),('experiments/llm_v2/human_review.csv',['fidelite_humaine']),('experiments/results/tp04/human_review.csv',['human_fidelity','human_safety']),('experiments/m01/human_review.csv',['human_score'])]:
 rows=list(csv.DictReader((ROOT/rel).open()));check('grille humaine préservée '+rel,not any(row.get(k,'').strip() for row in rows for k in fields))
# Contrôles négatifs d'import : aucun fichier de résultat humain n'est créé.
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'invalid.csv';p.write_text('key,dataset,case_id,configuration,reviewer,review_origin\nunknown,tp04,T01,mono_a,Codex,automated\n')
 try:validate(p);ok=False
 except ValueError:ok=True
 check('import refuse référence inventée / origine automatique',ok)
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8784'
def get(path):
 try:
  with urllib.request.urlopen(base+path,timeout=30) as r:return r.status,r.read(),r.headers
 except urllib.error.HTTPError as e:return e.code,e.read(),e.headers
code,data,_=get('/api/coursework');body=json.loads(data);check('index de remise huit blocs',code==200 and len(body['work'])==8)
for r in body['resources']:
 code,data,headers=get(r['href']);check('ressource disponible '+r['id'],r['available'] and code==200 and len(data)>50)
check('ressource inconnue refusée',get('/api/resources/not_allowed')[0]==404)
code,data,_=get('/api/policy');pol=json.loads(data);check('quotas réels et budget prospectif séparés',code==200 and pol['max_calls']==2 and pol['admission_concurrency']==1 and 'ND' in pol['cost_budget_status'])
code,data,_=get('/api/metrics');metrics=json.loads(data);check('FinOps allocation fictive explicite',len(metrics['allocated_scenario'])==4 and all('hypothétique' in r['status'] for r in metrics['allocated_scenario']))
check('relecture accessible sans annotation préremplie',get('/review')[0]==200)
(ROOT/'experiments/results/submission_checks.json').write_text(json.dumps(dict(checks=checks,total=len(checks),all_passed=all(c['passed'] for c in checks),new_inference=False,human_annotations_created=0),ensure_ascii=False,indent=2));print(len(checks),'contrôles de remise réussis')
