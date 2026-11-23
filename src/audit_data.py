"""Audit ARFF et partitions chronologiques, bibliothèque standard Python uniquement."""
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/raw/creditcard.arff'

def main():
    metadata = json.loads((SOURCE.parent / 'openml_1597_metadata.json').read_text())['data_set_description']
    digest = hashlib.sha256()
    md5 = hashlib.md5()
    with SOURCE.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
            md5.update(block)
    if md5.hexdigest() != metadata['md5_checksum']:
        raise ValueError('Empreinte différente de la référence OpenML : fichier incomplet ou modifié.')
    columns, records, seen = [], [], set()
    missing, invalid = Counter(), Counter()
    minima, maxima = {}, {}
    raw_classes, duplicate_classes = Counter(), Counter()
    data_started = False
    with SOURCE.open() as stream:
        for line in stream:
            line = line.strip()
            if not line or line.startswith('%'):
                continue
            if not data_started:
                if line.lower().startswith('@attribute'):
                    columns.append(line.split()[1].strip("'\""))
                if line.lower() == '@data':
                    data_started = True
                continue
            values = next(csv.reader([line]))
            if len(values) != len(columns):
                raise ValueError('Nombre de champs incorrect.')
            row_id = sum(raw_classes.values())
            numeric = []
            for name, value in zip(columns, values):
                if value == '?':
                    missing[name] += 1
                    numeric.append(None)
                    continue
                number = float(value.strip("\"'"))
                if not math.isfinite(number):
                    invalid[name] += 1
                minima[name] = min(minima.get(name, number), number)
                maxima[name] = max(maxima.get(name, number), number)
                numeric.append(number)
            label = numeric[columns.index('Class')]
            if label not in (0, 1):
                raise ValueError('Label absent ou invalide.')
            raw_classes[int(label)] += 1
            # Égalité numérique de toutes les colonnes, label et temps compris.
            key = hashlib.sha256(json.dumps(numeric).encode()).digest()
            if key in seen:
                duplicate_classes[int(label)] += 1
                continue
            seen.add(key)
            records.append((numeric[columns.index('Time')], row_id, int(label)))
    expected = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount', 'Class']
    if columns != expected or missing or invalid:
        raise ValueError(f'Schéma ou valeurs incompatibles : {columns}, {missing}, {invalid}')
    records.sort()
    # Toutes les transactions au même instant restent dans la même partition.
    boundary1 = records[int(len(records) * 0.6)][0]
    boundary2 = records[int(len(records) * 0.8)][0]
    if boundary1 >= boundary2:
        raise ValueError('Frontières temporelles impossibles.')
    target = ROOT / 'data/processed'
    target.mkdir(exist_ok=True)
    summaries = {}
    writers, streams = {}, []
    try:
        for split in ['train', 'validation', 'test']:
            stream = (target / f'{split}_indices.csv').open('w', newline='')
            streams.append(stream)
            writers[split] = csv.writer(stream)
            writers[split].writerow(['source_row_index'])
            summaries[split] = {'rows': 0, 'frauds': 0, 'time_min': None, 'time_max': None}
        for time, index, label in records:
            split = 'train' if time < boundary1 else 'validation' if time < boundary2 else 'test'
            writers[split].writerow([index])
            info = summaries[split]
            info['rows'] += 1
            info['frauds'] += label
            if info['time_min'] is None:
                info['time_min'] = time
            info['time_max'] = time
    finally:
        for stream in streams:
            stream.close()
    for info in summaries.values():
        info['fraud_rate'] = info['frauds'] / info['rows']
        if not 0 < info['frauds'] < info['rows']:
            raise ValueError('Une partition ne contient pas les deux classes.')
    assert sum(s['rows'] for s in summaries.values()) == len(records)
    assert summaries['train']['time_max'] < summaries['validation']['time_min']
    assert summaries['validation']['time_max'] < summaries['test']['time_min']
    report = dict(source_id=1597, source_version=metadata['version'], sha256=digest.hexdigest(),
                  md5_verified=True, raw_rows=sum(raw_classes.values()), raw_classes=dict(raw_classes),
                  removed_duplicate_classes=dict(duplicate_classes), retained_rows=len(records),
                  missing=dict(missing), nonfinite=dict(invalid), columns=columns,
                  ranges={k: [minima[k], maxima[k]] for k in columns}, splits=summaries,
                  index_convention='zero-based data row, excluding ARFF header',
                  duplicate_policy='keep first exact numeric full-row occurrence',
                  split_policy='chronological approximately 60/20/20, equal timestamps grouped')
    (ROOT / 'experiments/data_audit.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({k: report[k] for k in ['raw_rows','raw_classes','removed_duplicate_classes','retained_rows','splits','sha256']}, indent=2))

if __name__ == '__main__':
    main()
