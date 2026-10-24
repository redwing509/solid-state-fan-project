import json,shutil,subprocess,tarfile
from pathlib import Path
r=Path('/opt/fan-research/2026-10-21')
with tarfile.open(r/'queue/github-seed.tar.gz') as archive:archive.extractall(r/'github-seed',filter='data')
for name in ['TASKS.md','Project_To_Do.md','Validation_Plan.md','Simulation_Progress.md','Validation_Audit_2026-10-22.md']:
 shutil.copy2(r/'github-seed/docs'/name,r/name)
p=subprocess.run(['nice','-n','15','python3',str(r/'queue/github_result_publisher.py'),'--once'],timeout=180)
if p.returncode:raise SystemExit('Publisher returned nonzero')
s=json.loads((r/'queue/github_sync_status.json').read_text())
p=subprocess.run(['git','-C',str(r/'github-export'),'ls-remote','origin','refs/heads/simulation-results'],capture_output=True,text=True,timeout=40)
remote=p.stdout.split()[0] if p.returncode==0 and p.stdout.strip() else None
print(json.dumps({'state':s['state'],'exported_cases':len(s['exported_cases']),'remote_commit':remote,'verified':remote==s.get('latest_pushed_commit'),'safe_error':s.get('safe_error')}))
if s['state'] not in ['synced','complete'] or remote!=s.get('latest_pushed_commit'):raise SystemExit('Final backup not verified')
