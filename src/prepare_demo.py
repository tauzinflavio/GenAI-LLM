"""Reconstruire les artefacts de démonstration sans réécrire les résultats scientifiques archivés."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(script):
    subprocess.run([sys.executable,str(ROOT/'src'/script)],cwd=ROOT,check=True)

def rebuild_artifacts(required):
    # Le code calcule ROOT depuis son propre emplacement ; l'exécuter dans une racine isolée.
    with tempfile.TemporaryDirectory(prefix='fraudlab_prepare_') as directory:
        staging=Path(directory)
        (staging/'src').mkdir();shutil.copy2(ROOT/'src/run_experiment.py',staging/'src/run_experiment.py')
        shutil.copytree(ROOT/'configs',staging/'configs')
        (staging/'data').mkdir()
        # Liens en lecture : mêmes entrées auditées, aucun nouveau téléchargement implicite.
        (staging/'data/raw').symlink_to((ROOT/'data/raw').resolve(),target_is_directory=True)
        (staging/'data/processed').symlink_to((ROOT/'data/processed').resolve(),target_is_directory=True)
        subprocess.run([sys.executable,str(staging/'src/run_experiment.py')],cwd=staging,check=True)
        for relative in required:
            destination=ROOT/relative;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(staging/relative,destination)
        record={'method':'isolated reconstruction of demo artifacts; archived metrics unchanged',
                'config_sha256':hashlib.sha256((ROOT/'configs/experiment_v1.json').read_bytes()).hexdigest(),
                'artifacts':{relative:hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() for relative in required}}
        (ROOT/'data/local_preparation.json').write_text(json.dumps(record,indent=2))

def main():
    raw=ROOT/'data/raw'
    if not (raw/'creditcard.arff').exists() or not (raw/'openml_1597_metadata.json').exists():run('download_data.py')
    run('audit_data.py')
    required=['models/B1_class_weight_42.joblib','models/detector_scaler.joblib','experiments/v1/ddpm_42.pt',
              'experiments/v1/generator_scaler_42.joblib','experiments/v1/B1_class_weight_42_validation_scores.npy']
    if not all((ROOT/relative).exists() for relative in required):rebuild_artifacts(required)
    if not all(any((ROOT/'models'/role).glob('*.safetensors')) for role in ['writer','verifier']):run('download_llms.py')
    print('Préparation terminée. Lancer python scripts/serve.py. Résultats archivés préservés ; test final non réévalué.')
if __name__=='__main__':main()
