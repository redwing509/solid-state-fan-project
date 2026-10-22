import importlib.util
import json
from pathlib import Path
import tempfile

root=Path('/opt/fan-research/2026-10-21/queue')
spec=importlib.util.spec_from_file_location('fan_queue_worker',root/'fan_queue_worker.py')
worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
jobs=json.loads((root/'manifest.json').read_text())
passed=[]
with tempfile.TemporaryDirectory(prefix='preflight-',dir=root) as folder:
    for job in jobs:
        worker.validate(job)
        worker.prepare(job,Path(folder)/job['id'])
        passed.append(job['id'])
record={'validated_and_prepared_jobs':len(passed),'total_jobs':len(jobs),'passed':len(passed)==len(jobs),'note':'Input preparation only; no simulations launched by preflight'}
(root/'preflight.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record))
