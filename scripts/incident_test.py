"""Panne d'un processus modèle dans une instance jetable appartenant à ce script."""
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
from pathlib import Path
from service_checks import ROOT,call,smoke
BASE='http://127.0.0.1:8781'

def main():
    out=ROOT/'evidence';out.mkdir(exist_ok=True)
    log=(out/'incident_server.log').open('w')
    env={**os.environ,'FRAUDLAB_SERVING':'1'}
    command=[sys.executable,'-m','uvicorn','app:app','--app-dir',str(ROOT/'src'),'--host','127.0.0.1','--port','8781']
    process=None
    def start():
        return subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
    def ready():
        deadline=time.monotonic()+150
        while time.monotonic()<deadline:
            if process.poll() is not None:raise RuntimeError('service exited before ready')
            try:
                code,data,_=call(BASE,'/readyz')
                if code==200:return data
            except (OSError,urllib.error.URLError):pass
            time.sleep(.5)
        raise TimeoutError('readiness timeout')
    try:
        process=start();state=ready()
        before=smoke(BASE,out/'smoke_before_incident.json')
        worker=next(m for m in state['models'] if m['role']=='writer')
        assert state['service_pid']==process.pid, 'Le serveur testé doit appartenir à ce script.'
        assert isinstance(worker['pid'],int) and worker['pid']!=process.pid
        start_failure=time.perf_counter()
        os.kill(worker['pid'],signal.SIGTERM)
        time.sleep(.5)
        h,_,_=call(BASE,'/healthz');r,_,_=call(BASE,'/readyz')
        g,data,_=call(BASE,'/v1/generate',{'amount':20,'score':.1,'needs_review':False,'strategy':'mono_a'})
        assert (h,r,g)==(200,503,503),(h,r,g)
        process.terminate();process.wait(timeout=15)
        process=start();ready()
        after=smoke(BASE,out/'smoke_after_incident.json')
        recovery=time.perf_counter()-start_failure
        evidence={'fault':'SIGTERM du processus writer de cette seule instance jetable','cause_confirmed':'processus modèle arrêté volontairement',
            'health_during_http':h,'ready_during_http':r,'generate_during_http':g,
            'fallback_external':False,'recovery_action':'redémarrage complet du service local et warm-up des deux modèles',
            'recovery_seconds':recovery,'before':before,'after':after,
            'recovered':after['real_inference'] and after['inference_http']==200,'quality_after':after['contract_pass'],
            'limits':'Un incident local contrôlé ; aucun SLA ni disponibilité de production démontré.'}
        (out/'incident.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
        print('Reprise',round(recovery,2),'secondes',evidence['recovered'])
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        log.close()

if __name__=='__main__':main()
