"""Exécuter les notebooks pédagogiques Python sans serveur Jupyter.

Chaque cellule de code est réellement exécutée dans un espace de noms commun.
stdout, stderr, figures PNG et compteurs d'exécution sont intégrés au notebook.
Les sorties précédentes ne sont jamais utilisées pour calculer les suivantes.
"""
import base64,contextlib,hashlib,io,json,platform,time
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def execute(path):
    nb=json.loads(path.read_text());ns={'__name__':'__main__'};directory=ROOT/'experiments'/path.stem.split('_')[0].lower();directory.mkdir(parents=True,exist_ok=True)
    figures=[];counter=0;start=time.perf_counter()
    for cell in nb['cells']:
        if cell['cell_type']!='code':continue
        counter+=1;out=io.StringIO();err=io.StringIO();outputs=[]
        def show(*args,**kwargs):
            for number in plt.get_fignums():
                fig=plt.figure(number);name=f'figure_{len(figures)+1:02d}.png';file=directory/name
                fig.savefig(file,dpi=130,bbox_inches='tight');figures.append(str(file.relative_to(ROOT)))
                outputs.append({'output_type':'display_data','data':{'image/png':base64.b64encode(file.read_bytes()).decode(),'text/plain':[f'<Figure exportée : {name}>']},'metadata':{}})
            plt.close('all')
        plt.show=show
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):exec(compile(''.join(cell['source']),f'{path.name}:cellule{counter}','exec'),ns)
        if out.getvalue():outputs.insert(0,{'output_type':'stream','name':'stdout','text':out.getvalue().splitlines(True)})
        if err.getvalue():outputs.append({'output_type':'stream','name':'stderr','text':err.getvalue().splitlines(True)})
        cell.update(execution_count=counter,outputs=outputs)
        if 'À poursuivre' in out.getvalue():raise AssertionError('Vérification pédagogique échouée : '+out.getvalue())
    nb['metadata']['execution']={'method':'Python exec par cellule, sorties et figures capturées','python':platform.python_version(),'numpy':np.__version__,'code_cells':counter,'executed':True}
    path.write_text(json.dumps(nb,ensure_ascii=False,indent=1))
    evidence={'notebook':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__,'code_cells_executed':counter,'all_assertions_passed':True,'figures':figures,'seconds':time.perf_counter()-start,'scenario':'entièrement synthétique','authorship':'réalisation assistée par Codex ; contributions humaines non attribuées'}
    (directory/'execution.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print(json.dumps(evidence,ensure_ascii=False))
if __name__=='__main__':
    for name in ['TP01_FraudLab.ipynb','TP02_FraudLab.ipynb']:execute(ROOT/'notebooks'/name)
