"""Vérifie la réactivation HTTP après arrêt d'un worker d'une instance détenue par ce script."""
import json,os,signal,subprocess,sys,time,urllib.error
from service_checks import ROOT,call
BASE='http://127.0.0.1:8785'
def main():
    evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
    with (evidence/'recovery_server.log').open('w') as log:
        p=subprocess.Popen([sys.executable,str(ROOT/'scripts/serve.py'),'--port','8785'],stdout=log,stderr=subprocess.STDOUT)
        def wait_ready():
            end=time.monotonic()+150
            while time.monotonic()<end:
                if p.poll() is not None:raise RuntimeError('service exited')
                try:
                    code,data,_=call(BASE,'/readyz')
                    if code==200:return data
                except (OSError,urllib.error.URLError):pass
                time.sleep(.5)
            raise TimeoutError('recovery timeout')
        try:
            ready=wait_ready();assert ready['service_pid']==p.pid
            worker=next(m for m in ready['models'] if m['role']=='writer')
            os.kill(worker['pid'],signal.SIGTERM);time.sleep(.3)
            down,_,_=call(BASE,'/readyz');assert down==503
            start=time.perf_counter();status,_,_=call(BASE,'/api/recover',{});assert status==202
            wait_ready()
            code,result,_=call(BASE,'/v1/generate',{'amount':20,'score':.1,'needs_review':False,'strategy':'mono_b'})
            passed=code==200 and result.get('contract_pass') and result.get('calls')==1
            record={'controlled_fault':'writer terminated in owned disposable instance','ready_during_http':down,'recover_http':status,
                'recovery_and_real_inference_seconds':time.perf_counter()-start,'after_http':code,'after_contract_pass':bool(result.get('contract_pass')),
                'trace_id':result.get('trace_id'),'passed':bool(passed),'automatic_original_request_retry':False}
            (evidence/'recovery_endpoint.json').write_text(json.dumps(record,indent=2));assert passed;print(json.dumps(record,indent=2))
        finally:
            p.terminate()
            try:p.wait(timeout=15)
            except subprocess.TimeoutExpired:p.kill();p.wait()
if __name__=='__main__':main()
