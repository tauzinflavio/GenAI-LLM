"""Archive de partage à partir d'une liste de fichiers sans données, poids, base ou secrets."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT.parent/'FraudLab_code_et_rapports.zip'

def included(path):
    rel=path.relative_to(ROOT)
    if path.is_symlink() or not path.is_file():return False
    if any(p in {'__pycache__','.git','.venv','models','backups'} for p in rel.parts):return False
    if rel.parts[:2] in [('data','raw'),('data','processed')]:return False
    if path.suffix in {'.pt','.pth','.joblib','.npy','.sqlite','.log','.pyc'} or '.sqlite-' in path.name:return False
    if path.name.startswith('.env') and path.name!='.env.example':return False
    if path.name.startswith('synthetic_') or path.name=='local_preparation.json':return False
    if path.name=='MANIFEST.sha256':return False
    return True

def main():
    files=sorted(p for p in ROOT.rglob('*') if included(p))
    # Vérification JSON stricte de toutes les preuves partagées, sans interpréter les sorties modèles.
    for path in files:
        if path.suffix=='.json':
            def reject(v):raise ValueError(f'Non-finite JSON in {path.name}: {v}')
            json.loads(path.read_text(),parse_constant=reject)
    manifest=''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in files)
    (ROOT/'MANIFEST.sha256').write_text(manifest)
    with zipfile.ZipFile(ARCHIVE,'w',zipfile.ZIP_DEFLATED) as archive:
        for path in files+[ROOT/'MANIFEST.sha256']:archive.write(path,ROOT.name+'/'+path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        for info in archive.infolist():
            assert '/models/' not in info.filename and '/data/raw/' not in info.filename and '/data/processed/' not in info.filename
            assert info.file_size<20_000_000,(info.filename,info.file_size)
    print(json.dumps({'archive':str(ARCHIVE),'files':len(files)+1,'bytes':ARCHIVE.stat().st_size,'sha256':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':main()
