"""Importer des annotations réellement déclarées par leurs auteurs, sans écraser les scores.

Une signature de formulaire n'est pas une vérification d'identité. Utiliser --dry-run
pour contrôler un export sans créer une campagne. Toute campagne existante est préservée.
"""
import argparse,csv,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(path):
    index={r['key']:r for r in json.loads((ROOT/'configs/review_index.json').read_text())}
    rows=list(csv.DictReader(Path(path).open(encoding='utf-8-sig')))
    if not rows:raise ValueError('Aucune annotation dans ce CSV.')
    seen=set()
    for row in rows:
        ref=index.get(row.get('key'))
        if ref is None or any(row.get(k)!=ref[k] for k in ['dataset','case_id','configuration']):raise ValueError('Référence de sortie inconnue ou modifiée.')
        reviewer=row.get('reviewer','').strip()
        if not reviewer or len(reviewer)>80 or row.get('review_origin')!='human_declared':raise ValueError('Annotateur et origine humaine déclarée requis.')
        for field,values in {'fidelity':{'conforme','partiellement_conforme','non_conforme','non_evaluable'},'omissions':{'aucune','mineures','majeures','non_evaluable'},'safety':{'conforme','non_conforme','non_evaluable'},'format':{'conforme','non_conforme','non_evaluable'}}.items():
            if row.get(field) not in values:raise ValueError('Note non autorisée : '+field)
        if not row.get('comment','').strip() or len(row['comment'])>2000:raise ValueError('Justification de 1 à 2000 caractères requise.')
        datetime.fromisoformat(row.get('reviewed_at','').replace('Z','+00:00'))
        key=(row['key'],reviewer)
        if key in seen:raise ValueError('Annotation en double pour le même auteur et la même sortie.')
        seen.add(key)
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--dry-run',action='store_true');p.add_argument('--campaign',default=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));a=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',a.campaign):raise ValueError('Nom de campagne invalide.')
    rows=validate(a.csv);summary={'annotations':len(rows),'annotators':sorted({r['reviewer'] for r in rows}),'datasets':sorted({r['dataset'] for r in rows}),'origin':'human_declared, identité non certifiée','source_sha256':hashlib.sha256(Path(a.csv).read_bytes()).hexdigest(),'automatic_scores_unchanged':True}
    if not a.dry_run:
        destination=ROOT/'experiments/human_review'/a.campaign;destination.mkdir(parents=True,exist_ok=False)
        with (destination/'annotations.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        (destination/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
