from pathlib import Path
r=Path('/opt/fan-research/2026-10-21');p=r/'queue/cases/esp-f0f62e28a1'
for n in ['0/U','0/p','constant/electricProperties','0/rhoq']:
 print('FILE',n,(p/n).read_text()[:5500])
for n in ['createFields.H','UEqn.H']:
 for p in (r/'modern-ehd/source').rglob(n):
  if 'lnInclude' not in p.parts:print('SOURCE',p,p.read_text()[:6500])
