"""Vérifie références obligatoires et cohérence des résultats, sans inférence."""
import ast,csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
required=['README.md','requirements.txt','src/orchestrator.py','src/app.py','docs/04_poc_v1_plan_v2.md','docs/05_tp04_architecture_v2.md','docs/05_tp04_benchmark.md','docs/06_tp05_finops_green_ethique.md','docs/deployment_decision.md','docs/incident_runbook.md','evidence/smoke.json','evidence/incident.json','evidence/recovery_endpoint.json','outputs/load_c1.csv','outputs/load_c3.csv','deliverables/C2_Cadrage_FraudLab.pdf','deliverables/C3_Preuve_technique_FraudLab.pdf','deliverables/Rapport_consolide_FraudLab.pdf','deliverables/TPM01_Comparaison_FraudLab.pdf']
for path in required:assert (ROOT/path).is_file(),path
for directory in ['src','scripts','tests']:
 for path in (ROOT/directory).glob('*.py'):ast.parse(path.read_text())
rows=list(csv.DictReader((ROOT/'experiments/results/tp04/summary.csv').open()))
assert {r['strategy'] for r in rows}=={'mono_a','mono_b','routing','cascade'}
assert all(int(r['cases'])==10 for r in rows)
traces=[json.loads(line) for line in (ROOT/'experiments/results/tp04/traces.jsonl').read_text().splitlines()]
assert len(traces)==40
assert all(r['calls']<=2 and len(r['traces'])==r['calls'] for r in traces)
for row in rows:
 arm=[r for r in traces if r['strategy']==row['strategy']]
 assert sum(r['contract_pass'] for r in arm)==int(row['passes'])
 assert sum(r['calls'] for r in arm)==int(row['calls'])
protocol=json.loads((ROOT/'experiments/results/tp04/protocol.json').read_text())
for name,key in [('orchestrator.py','orchestrator_sha256'),('benchmark_tp04.py','benchmark_sha256')]:
 assert hashlib.sha256((ROOT/'experiments/results/tp04/code'/name).read_bytes()).hexdigest()==protocol[key]
for path in ['evidence/incident.json','evidence/recovery_endpoint.json','evidence/backup_restore.json']:
 record=json.loads((ROOT/path).read_text());assert record.get('passed',record.get('recovered')),path
for path in ['experiments/application_checks_latest.json','experiments/results/service_safety.json','experiments/results/tp04_robustness.json']:
 record=json.loads((ROOT/path).read_text());checks=record['checks'] if isinstance(record,dict) else record;assert all(r['passed'] for r in checks),path
print('Dossier et preuves cohérents ; validation humaine et GitHub restent distincts.')
