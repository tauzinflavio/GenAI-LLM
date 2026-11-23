"""POC local interface–API–SQLite. Lancer sur 127.0.0.1 uniquement."""
import json
import os
import time
import hashlib
from contextlib import asynccontextmanager
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
import pandas as pd
import torch
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from scipy.io import arff

from benchmark_llm import assess
from run_experiment import NoisePredictor, sample_diffusion
from orchestrator import ModelWorker, Orchestrator, expected_report, Policy
from dataclasses import asdict

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data/local_app.sqlite'
WORKERS = {}
RECOVERING = False
SERVICE_LOCK = threading.Lock()

@asynccontextmanager
async def lifespan(app):
    # Backend chargé avant disponibilité du service. Aucun téléchargement au démarrage.
    if os.environ.get('FRAUDLAB_SERVING', '0') == '1':
        for role in ['writer','verifier']:
            worker=ModelWorker(role)
            try:
                worker.start()
                WORKERS[role]=worker
            except (OSError, RuntimeError, TimeoutError):
                worker.close()
    yield
    for worker in WORKERS.values():
        worker.close()

app = FastAPI(title='FraudLab ECE — prototype local', version='0.2', lifespan=lifespan)
LOCK = threading.Lock()
MODEL = joblib.load(ROOT / 'models/B1_class_weight_42.joblib')
SCALER = joblib.load(ROOT / 'models/detector_scaler.joblib')
METRICS = pd.read_csv(ROOT / 'experiments/v1/metrics.csv')
THRESHOLD = float(METRICS[(METRICS.configuration == 'B1_class_weight') & (METRICS.seed == 42)].threshold.iloc[0])
with sqlite3.connect(DB) as connection:
    connection.execute('CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, created TEXT, kind TEXT, payload TEXT)')


def persist(kind, payload):
    event_id = str(uuid.uuid4())
    with sqlite3.connect(DB, timeout=20) as connection:
        connection.execute("DELETE FROM events WHERE created < ?", ((datetime.now(timezone.utc)-__import__('datetime').timedelta(days=30)).isoformat(),))
        connection.execute('INSERT INTO events VALUES (?, ?, ?, ?)',
                           (event_id, datetime.now(timezone.utc).isoformat(), kind, json.dumps(payload, allow_nan=False)))
    return event_id


@app.middleware('http')
async def local_only(request: Request, call_next):
    if request.headers.get('host','').split(':')[0] not in {'localhost','127.0.0.1','testserver'}:
        return JSONResponse({'detail':'Hôte local requis'}, status_code=403)
    origin = request.headers.get('origin')
    if origin and origin not in {f'http://{request.headers.get("host")}'}:
        return JSONResponse({'detail':'Origine différente refusée'},status_code=403)
    try:
        length = int(request.headers.get('content-length', '0'))
    except ValueError:
        return JSONResponse({'detail':'Longueur de requête invalide'},status_code=400)
    if length < 0:
        return JSONResponse({'detail':'Longueur de requête invalide'},status_code=400)
    if length > 100000:
        return JSONResponse({'detail':'Requête trop volumineuse'},status_code=413)
    if request.method == 'POST':
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 100000:
                return JSONResponse({'detail':'Requête trop volumineuse'},status_code=413)
        try:
            # JSON standard exclut NaN et Infinity, qui cassent aussi la sérialisation des erreurs.
            def reject_constant(value):
                raise ValueError(value)
            json.loads(body, parse_constant=reject_constant)
        except (ValueError, UnicodeDecodeError):
            return JSONResponse({'detail':'Corps JSON invalide ou valeur non finie'},status_code=400)
        request._body = bytes(body)
    return await call_next(request)


class Transaction(BaseModel):
    model_config = ConfigDict(extra='forbid')
    features: list[float] = Field(min_length=29,max_length=29)
    reference: str = Field(default='saisie_locale',max_length=80,pattern=r'^[A-Za-z0-9_-]+$')

    @field_validator('features')
    @classmethod
    def valid_features(cls, value):
        if not np.isfinite(value).all() or value[-1] < 0 or np.abs(value).max() > 1e12:
            raise ValueError('29 valeurs finies requises, montant non négatif, amplitude <= 1e12.')
        return value


class Generation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    count: int = Field(default=4,ge=1,le=32)
    seed: int = Field(default=42,ge=0,le=99999)


class Analysis(BaseModel):
    model_config = ConfigDict(extra='forbid')
    prediction_id: str = Field(max_length=80)
    mode: Literal['template','mono_a','mono_b','routing','cascade'] = 'template'


class Decision(BaseModel):
    model_config = ConfigDict(extra='forbid')
    prediction_id: str = Field(max_length=80)
    action: Literal['approfondir','classer']


def find_prediction(event_id):
    with sqlite3.connect(DB) as connection:
        row = connection.execute('SELECT payload FROM events WHERE id=? AND kind=?',(event_id,'prediction')).fetchone()
    if row is None:
        raise HTTPException(404,'Prédiction introuvable')
    return json.loads(row[0])


@app.get('/')
def index():
    return FileResponse(ROOT / 'app/index.html')


@app.get('/api/status')
def status():
    llm_summary = ROOT / 'experiments/llm_v1/summary.csv'
    return dict(detector='B1_class_weight',seed=42,threshold=THRESHOLD,
                threshold_policy='F1 sur validation, exploratoire',score_calibrated=False,test_evaluated=(ROOT/'experiments/final_test/metrics.csv').exists(),
                llms_ready=all(any((ROOT/'models'/role).glob('*.safetensors')) for role in ['writer','verifier']),
                llm_benchmark_ready=llm_summary.exists(),serving_ready=not RECOVERING and all(role in WORKERS and WORKERS[role].alive() for role in ['writer','verifier']),access='local_simulated_analyst')


@app.get('/api/metrics')
def metrics():
    summary = METRICS.groupby('configuration').average_precision.agg(['mean','std']).reset_index()
    llm = ROOT / 'experiments/llm_v1/summary.csv'
    llm_v2 = ROOT / 'experiments/llm_v2/summary.csv'
    tp04 = ROOT / 'experiments/results/tp04/summary.csv'
    tp05 = ROOT / 'experiments/results/tp05_mesures_tp04.csv'
    def rows(path):
        return json.loads(pd.read_csv(path).to_json(orient='records')) if path.exists() else []
    load_files=sorted((ROOT/'outputs').glob('load_*.json'))
    loads=[json.loads(path.read_text()) for path in load_files]
    return dict(financial_scenarios=rows(ROOT/'experiments/results/financial_breakdown.csv'),allocated_scenario=rows(ROOT/'experiments/results/finops_allocated_scenario.csv'),tp04=rows(tp04),tp05=rows(tp05),deployment=loads,llm_v2=pd.read_csv(llm_v2).to_dict(orient='records') if llm_v2.exists() else [],
                genai=summary.to_dict(orient='records'),
                final=pd.read_csv(ROOT/'experiments/final_test/metrics.csv').to_dict(orient='records') if (ROOT/'experiments/final_test/metrics.csv').exists() else [],
                generation=pd.read_csv(ROOT/'experiments/v1/generation_metrics.csv').to_dict(orient='records'),
                llm=pd.read_csv(llm).to_dict(orient='records') if llm.exists() else [])


@app.get('/api/cases')
def cases():
    # Démonstration sur validation uniquement ; label réel exclu de l'API et des prompts.
    raw,_=arff.loadarff(ROOT/'data/raw/creditcard.arff')
    data=pd.DataFrame(raw)
    ids=pd.read_csv(ROOT/'data/processed/validation_indices.csv').source_row_index.to_numpy()
    scores=np.load(ROOT/'experiments/v1/B1_class_weight_42_validation_scores.npy')
    order=np.argsort(scores)
    selected=np.concatenate([order[-6:][::-1],order[:4]])
    result=[]
    for i in selected:
        row=data.iloc[int(ids[i])]
        result.append(dict(reference=f'VAL-{int(ids[i])}',features=[float(row[f'V{k}']) for k in range(1,29)]+[float(row.Amount)]))
    return result


@app.post('/api/predict')
def predict(transaction: Transaction):
    raw=np.asarray(transaction.features,dtype=float).reshape(1,-1)
    prepared=raw.copy()
    prepared[:,-1]=np.log1p(prepared[:,-1])
    score=float(MODEL.predict_proba(SCALER.transform(prepared))[0,1])
    result=dict(reference=transaction.reference,amount=float(raw[0,-1]),score=score,needs_review=score>=THRESHOLD,
                detector='B1_class_weight_42',threshold=THRESHOLD,score_calibrated=False)
    stored={k:v for k,v in result.items() if k!='reference'}
    stored['reference_sha256']=hashlib.sha256(result['reference'].encode()).hexdigest()
    event_id=persist('prediction',stored)
    return dict(id=event_id,**result)


@app.post('/api/analyze')
def analyze(request: Analysis):
    prediction=find_prediction(request.prediction_id)
    facts={k:prediction[k] for k in ['amount','score','needs_review']}
    if request.mode == 'template':
        text=json.dumps(dict(amount=facts['amount'],score=facts['score'],country='unknown',
                            action='review' if facts['needs_review'] else 'abstain'))
        result=dict(mode='template',text=text,seconds=0,execution='règle déterministe',facts=facts)
    else:
        case={'id':'APP','category':'interactive','facts':facts,'expected':expected_report(facts),'complex':False}
        if not SERVICE_LOCK.acquire(blocking=False):
            raise HTTPException(429,'Une analyse est en cours. Réessayer après sa fin.')
        try:
            if not all(role in WORKERS and WORKERS[role].alive() for role in ['writer','verifier']):
                raise HTTPException(503,'Les modèles sont indisponibles. Relancer le service local.')
            record=Orchestrator(WORKERS).run(case,request.mode)
        finally:
            SERVICE_LOCK.release()
        result=dict(mode=request.mode,text=json.dumps(record['report']),seconds=record['seconds'],facts=facts,
                    execution='orchestration locale bornée · prompt V2',orchestration=record)
    result['checks']=assess(result['text'],facts)
    result['contract_valid']=result['checks']['all_checks'] and result.get('orchestration',{}).get('contract_pass',True)
    event_id=persist('analysis',dict(prediction_id=request.prediction_id,**result))
    return dict(id=event_id,**result)


@app.post('/api/decision')
def decision(request: Decision):
    find_prediction(request.prediction_id)
    event_id=persist('human_decision',request.model_dump())
    return dict(id=event_id,status='enregistré')


@app.post('/api/generate')
def generate(request: Generation):
    config=json.loads((ROOT/'configs/experiment_v1.json').read_text())['ddpm']
    with LOCK:
        model=NoisePredictor(29,config['hidden_size'])
        model.load_state_dict(torch.load(ROOT/'experiments/v1/ddpm_42.pt',weights_only=True,map_location='cpu'))
        model.eval()
        scaler=joblib.load(ROOT/'experiments/v1/generator_scaler_42.joblib')
        beta=torch.linspace(config['beta_start'],config['beta_end'],config['timesteps'])
        alpha=1-beta
        cumulative=torch.cumprod(alpha,dim=0)
        samples,elapsed=sample_diffusion(model,scaler,beta,alpha,cumulative,request.count,request.seed)
    valid=np.isfinite(samples).all(axis=1)&(samples[:,-1]>=0)&(samples[:,-1]<=np.log1p(1e9))
    accepted=samples[valid].copy()
    accepted[:,-1]=np.expm1(accepted[:,-1])
    result=dict(seed=request.seed,requested=request.count,accepted=int(valid.sum()),rejected=int((~valid).sum()),
                seconds=elapsed,features=accepted.tolist(),columns=[f'V{i}' for i in range(1,29)]+['Amount'],
                model='DDPM fraude seule seed42, 100 pas',synthetic=True)
    event_id=persist('generation',result)
    return dict(id=event_id,**result)


@app.get('/api/history')
def history():
    with sqlite3.connect(DB) as connection:
        rows=connection.execute('SELECT id,created,kind,payload FROM events ORDER BY rowid DESC LIMIT 50').fetchall()
    return [dict(id=i,created=t,kind=k,payload=json.loads(p)) for i,t,k,p in rows]


@app.get('/healthz')
def healthz():
    return {'status':'alive','service':'fraudlab','version':'0.2'}

@app.get('/readyz')
def readyz():
    ready=not RECOVERING and all(role in WORKERS and WORKERS[role].alive() for role in ['writer','verifier'])
    models=json.loads((ROOT/'configs/llm_models.json').read_text())
    result={'service_pid':os.getpid(),'status':'ready' if ready else 'not_ready','backend':'local_transformers_processes',
            'models':[{ 'role':role,'model_id':models[role]['model_id'],'revision':models[role]['revision'],
                       'alive':bool(role in WORKERS and WORKERS[role].alive()),
                       'pid':WORKERS[role].process.pid if role in WORKERS and WORKERS[role].process else None}
                      for role in ['writer','verifier']]}
    return JSONResponse(result,status_code=200 if ready else 503)

class ServiceGeneration(BaseModel):
    model_config=ConfigDict(extra='forbid')
    amount: float | None = Field(default=20,ge=0,le=1e9,allow_inf_nan=False)
    score: float | None = Field(default=0.1,ge=0,le=1,allow_inf_nan=False)
    needs_review: bool = False
    strategy: Literal['mono_a','mono_b','routing','cascade']='mono_b'

@app.post('/v1/generate')
def service_generate(request: ServiceGeneration):
    # Un seul traitement à la fois ; rejet plutôt que file d'attente non bornée.
    if not SERVICE_LOCK.acquire(blocking=False):
        raise HTTPException(429,'Capacité locale occupée ; aucun retry automatique.')
    try:
        if not all(role in WORKERS and WORKERS[role].alive() for role in ['writer','verifier']):
            raise HTTPException(503,'Backend de modèles indisponible ; aucun transfert externe.')
        facts=request.model_dump(exclude={'strategy'})
        case={'id':'SERVICE','category':'usual','facts':facts,'expected':expected_report(facts)}
        record=Orchestrator(WORKERS).run(case,request.strategy)
        # Journal minimal : aucune entrée, sortie libre, référence ou identifiant personnel.
        persist('service_generation',dict(trace_id=record['trace_id'],strategy=request.strategy,status=record['status'],
                calls=record['calls'],seconds=record['seconds'],contract_pass=record['contract_pass']))
        if record['status']=='failed':
            code=504 if record['reason'] in {'timeout','request_timeout'} else 502
            return JSONResponse({'trace_id':record['trace_id'],'status':record['status'],'reason':record['reason'],
                'contract_pass':False,'report':record['report']},status_code=code)
        return record
    finally:
        SERVICE_LOCK.release()


def restart_failed_workers():
    global RECOVERING
    try:
        for role in ['writer','verifier']:
            if role not in WORKERS or not WORKERS[role].alive():
                worker=WORKERS.get(role) or ModelWorker(role)
                WORKERS[role]=worker
                worker.start()
        persist('backend_recovery',{'status':'ready'})
    except (OSError,RuntimeError,TimeoutError):
        persist('backend_recovery',{'status':'failed'})
    finally:
        SERVICE_LOCK.release()
        RECOVERING=False

@app.post('/api/recover')
def recover(background_tasks: BackgroundTasks):
    global RECOVERING
    if not SERVICE_LOCK.acquire(blocking=False):
        raise HTTPException(429,'Une opération est en cours. Réessayer après sa fin.')
    RECOVERING=True
    background_tasks.add_task(restart_failed_workers)
    return JSONResponse({'status':'restarting','note':'Chargement local ; aucune requête précédente rejouée.'},status_code=202)


# Ressources de remise : liste fermée, aucun accès à un chemin fourni par l'utilisateur.
RESOURCES = {
    'tp01': ('notebooks/TP01_FraudLab.ipynb', 'Notebook TP01 exécuté'),
    'tp02': ('notebooks/TP02_FraudLab.ipynb', 'Notebook TP02 exécuté'),
    'tp_synthesis': ('deliverables/TP01_TP02_Synthese_FraudLab.pdf', 'Synthèse TP01 et TP02'),
    'c2': ('deliverables/C2_Cadrage_FraudLab.pdf', 'Cadrage C2'),
    'c3': ('deliverables/C3_Preuve_technique_FraudLab.pdf', 'Preuve C3'),
    'architecture': ('deliverables/Architecture_ADR_FraudLab.pdf', 'Architecture et décision une page'),
    'report': ('deliverables/Rapport_consolide_FraudLab.pdf', 'Rapport consolidé'),
    'model_card': ('docs/MODEL_CARD.md', 'Fiche modèle / système'),
    'matrix': ('docs/30_matrice_TP_projet_final.md', 'Tableau de suivi TP et projet'),
    'review': ('deliverables/Relecture_LLM.html', 'Atelier de relecture humaine'),
    'm01': ('deliverables/TPM01_Comparaison_FraudLab.pdf', 'Comparaison M01'),
}

@app.get('/api/resources/{resource_id}')
def resource(resource_id: str):
    entry = RESOURCES.get(resource_id)
    if not entry or not (ROOT / entry[0]).is_file():
        raise HTTPException(404, 'Ressource introuvable')
    path = ROOT / entry[0]
    return FileResponse(path, filename=path.name, content_disposition_type='inline' if path.suffix in {'.pdf','.html'} else 'attachment')

@app.get('/review')
def review_workbench():
    return FileResponse(ROOT / 'deliverables/Relecture_LLM.html')

@app.get('/api/coursework')
def coursework():
    return dict(project='FraudLab', team=json.loads((ROOT/'configs/team.json').read_text()),
        resources=[dict(id=k,title=v[1],href='/api/resources/'+k,available=(ROOT/v[0]).is_file()) for k,v in RESOURCES.items()],
        work=json.loads((ROOT/'configs/submission_status.json').read_text()),
        human_review='À réaliser par le groupe ; aucune annotation humaine créée automatiquement.',
        excluded=['Soutenance','PowerPoint'])

@app.get('/api/policy')
def policy_status():
    live=status()
    return dict(**asdict(Policy()), admission_concurrency=1, max_output_tokens=100, external_fallback=False,
        serving_ready=live['serving_ready'],cost_budget_eur_prospective=.35,cost_budget_status='objectif prospectif, coût complet réel ND, pas quota monétaire mesuré',
        operator='personne lançant la démonstration ; désignation nominative à décider',alert_channel='écran local et runbook ; aucun envoi externe',
        stops='429 si capacité occupée ; refus avant dépassement du budget tokens/appels ; worker interrompu à timeout')
