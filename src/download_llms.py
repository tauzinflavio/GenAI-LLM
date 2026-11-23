"""Obtenir deux modèles ouverts et figer leurs révisions dans le cache local."""
import json
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download

ROOT = Path(__file__).resolve().parents[1]
MODELS = {'writer': 'HuggingFaceTB/SmolLM2-360M-Instruct', 'verifier': 'Qwen/Qwen2.5-0.5B-Instruct'}

if __name__ == '__main__':
    config_path = ROOT / 'configs/llm_models.json'
    existing = json.loads(config_path.read_text()) if config_path.exists() else {}
    output = {}
    for role, model_id in MODELS.items():
        info = HfApi().model_info(model_id, revision=existing.get(role, {}).get('revision', 'main'))
        path = ROOT / 'models' / role
        snapshot_download(model_id, revision=info.sha, local_dir=path,
                          allow_patterns=['*.json', '*.safetensors', '*.txt', '*.model', 'LICENSE*', 'README.md'])
        output[role] = dict(model_id=model_id, revision=info.sha, local_path=f'models/{role}',
                            declared_license='apache-2.0', source=f'https://huggingface.co/{model_id}')
        (ROOT / 'configs/llm_models.json').write_text(json.dumps(output, indent=2))
        print(role, model_id, info.sha, flush=True)
