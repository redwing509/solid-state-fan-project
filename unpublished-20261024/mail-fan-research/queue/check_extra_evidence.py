import json
from pathlib import Path
q=Path('/opt/fan-research/2026-10-21/queue');m={j['id'] for j in json.loads((q/'manifest.json').read_text())};s=json.loads((q/'github_sync_status.json').read_text())
for identifier in set(s['exported_cases'])-m:
 p=q/'cases'/identifier
 print(json.dumps({'extra_case':identifier,'job':json.loads((p/'job.json').read_text()),'result':json.loads((p/'result.json').read_text())}))
