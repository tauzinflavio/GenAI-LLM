"""Lanceur local : mode service explicite, quatre threads CPU et aucun téléchargement."""
import argparse
import os
import sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8784);a=p.parse_args()
if not 1024<=a.port<=65535:raise SystemExit('Port local attendu entre 1024 et 65535')
os.environ['FRAUDLAB_SERVING']='1'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
if __name__=='__main__':
    import torch,uvicorn
    torch.set_num_threads(4)
    uvicorn.run('app:app',host='127.0.0.1',port=a.port)
