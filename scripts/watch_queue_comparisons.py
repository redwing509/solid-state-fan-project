import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime,timezone

root=Path('/opt/fan-research/2026-10-21/queue')
def record(**values):
    values['updated_at']=datetime.now(timezone.utc).isoformat()
    tmp=root/'analysis_status.tmp';tmp.write_text(json.dumps(values,indent=2));tmp.replace(root/'analysis_status.json')

with (root/'analysis.lock').open('a') as lock:
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise SystemExit('Comparison watcher already running')
    previous=None;failures=0;started=time.monotonic()
    while time.monotonic()-started<72*3600:
        status=json.loads((root/'status.json').read_text())
        complete=tuple(sorted((key,value['status']) for key,value in status['jobs'].items() if value['status']!='running'))
        if complete!=previous:
            env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
            try:
                with (root/'analysis.log').open('w') as log:
                    result=subprocess.run([sys.executable,str(root/'compare_snapshot.py')],stdout=log,stderr=subprocess.STDOUT,env=env,timeout=60)
                failures=0 if result.returncode==0 else failures+1
                if result.returncode==0:previous=complete
                record(state='watching' if result.returncode==0 else 'comparison_error',records_seen=len(complete),consecutive_errors=failures,last_exit_code=result.returncode)
            except subprocess.TimeoutExpired:
                failures+=1;record(state='comparison_timeout',records_seen=len(complete),consecutive_errors=failures)
            if failures>=3:
                record(state='stopped_for_review',reason='Three comparison failures',records_seen=len(complete));break
        if status['state'] in ['finished','finished_with_paused_families','stopped','waiting']:
            record(state='finished_snapshot',queue_state=status['state'],records_seen=len(complete));break
        time.sleep(60)
    else:record(state='time_limit',reason='72-hour comparison watcher cap')
