from pathlib import Path
import json
r=Path('/opt/fan-research/2026-10-21');q=r/'queue'
print('QUEUE',json.loads((q/'status.json').read_text())['state'])
base=r/'modern-ehd/source/examples/coaxialCorona'
for name in ['system/blockMeshDict','system/sample','constant/electricProperties','system/controlDict']:
 p=base/name;print('\nFILE',p);print(p.read_text()[:6500] if p.exists() else 'missing')
case=q/'cases/coaxial-2af5472879'
for p in sorted((case/'postProcessing/sample').glob('*/*.xy'))[-1:]:print('SAMPLE',p,'\n','\n'.join(p.read_text().splitlines()[:4]))
m=json.loads((q/'manifest.json').read_text())
for family in ['esp','legacy']:
 j=next(j for j in m if j['family']==family);p=q/'cases'/j['id'];print('CASE',family,p);print('CONTENTS',[x.name for x in p.iterdir()]);print('RESULT',(p/'result.json').read_text()[:2000])
 for n in ['constant/polyMesh/boundary','system/controlDict']:
  print(n,(p/n).read_text()[:5000])
 print('LATEST',sorted([x.name for x in p.iterdir() if x.is_dir() and x.name.replace('.','',1).isdigit()],key=float)[-2:])
for p in (r/'legacy-ehd').rglob('TEqn.H'):print('THERMAL_EQUATION',p,p.read_text())
