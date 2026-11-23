"""Télécharger la version OpenML utilisée et vérifier son intégrité."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
METADATA_URL = 'https://www.openml.org/api/v1/json/data/1597'
DATA_URL = 'https://openml.org/data/v1/download/1673544/creditcard.arff'


def main():
    destination = ROOT / 'data/raw'
    destination.mkdir(parents=True, exist_ok=True)
    with urlopen(METADATA_URL, timeout=60) as response:
        metadata_bytes = response.read()
    metadata = json.loads(metadata_bytes)['data_set_description']
    if metadata['version'] != '1' or metadata['url'] != DATA_URL:
        raise ValueError('La version ou la source OpenML a changé.')
    final_path = destination / 'creditcard.arff'
    temporary = destination / 'creditcard.arff.part'
    checksum = hashlib.md5()
    try:
        with urlopen(DATA_URL, timeout=600) as response, temporary.open('wb') as output:
            for block in iter(lambda: response.read(1024 * 1024), b''):
                checksum.update(block)
                output.write(block)
        if checksum.hexdigest() != metadata['md5_checksum']:
            raise ValueError('Empreinte différente de celle publiée par OpenML.')
        temporary.replace(final_path)
        (destination / 'openml_1597_metadata.json').write_bytes(metadata_bytes)
    finally:
        temporary.unlink(missing_ok=True)
    print('Données téléchargées et empreinte vérifiée. Lancer src/audit_data.py.')


if __name__ == '__main__':
    main()
