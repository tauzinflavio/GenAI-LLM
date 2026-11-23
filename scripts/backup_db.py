"""Sauvegarde SQLite cohérente et vérification d'une restauration dans une base neuve."""
import argparse,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--backup',default='data/backups/activity.sqlite');p.add_argument('--check',action='store_true');a=p.parse_args()
source=ROOT/'data/local_app.sqlite';target=ROOT/a.backup
target.parent.mkdir(parents=True,exist_ok=True)
if target.exists():raise SystemExit('Destination existante : choisir un nouveau nom pour conserver les sauvegardes.')
with sqlite3.connect(source) as src,sqlite3.connect(target) as dst:
    count=src.execute('SELECT count(*) FROM events').fetchone()[0];src.backup(dst)
    copied=dst.execute('SELECT count(*) FROM events').fetchone()[0]
    integrity=dst.execute('PRAGMA integrity_check').fetchone()[0]
if a.check:
    restored=target.with_name(target.stem+'_restore.sqlite')
    if restored.exists():raise SystemExit('Base de restauration déjà présente')
    with sqlite3.connect(target) as src,sqlite3.connect(restored) as dst:
        src.backup(dst);restored_count=dst.execute('SELECT count(*) FROM events').fetchone()[0]
    evidence={'source_rows':count,'backup_rows':copied,'restored_rows':restored_count,'integrity':integrity,'passed':count==copied==restored_count and integrity=='ok','scope':'restauration vers un fichier neuf ; aucune donnée existante écrasée'}
    (ROOT/'evidence/backup_restore.json').write_text(json.dumps(evidence,indent=2))
    assert evidence['passed']
    print(json.dumps(evidence,indent=2))
