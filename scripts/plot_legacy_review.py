import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out=Path('outputs/legacy-review')
s=json.loads((out/'legacy_review.json').read_text())
rows=list(csv.DictReader((out/'heated_wall_profile.csv').open()))
x=[float(r['x_m'])*1000 for r in rows]
t=[float(r['temperature_10s_k'])-273.15 for r in rows]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,(a,b)=plt.subplots(1,2,figsize=(10.8,4.5),gridspec_kw={'width_ratios':[1,1.5]})
vals=[s['thermal_audit']['effective_heat_flux_w_m2'],187]
a.bar(['Implied by\nexecuted equations','Documented\nreference'],vals,color=['#307d7e','#a4adb5'],width=.55)
for i,v in enumerate(vals):a.text(i,v+4,f'{v:.2f}',ha='center',fontweight='bold')
a.set_ylim(0,225);a.set_ylabel('Heat flux (W/m²)');a.set_title('Thermal inputs differ by 31.9%')
b.plot(x,t,color='#307d7e',linewidth=2)
b.set_xlabel('Distance along heated half-plate (mm)');b.set_ylabel('Calculated wall temperature (°C)')
b.set_title('Saved result at simulation time 10 s')
b.grid(alpha=.2)
fig.suptitle('Legacy EHD benchmark: completed execution, validation still open',fontsize=13,fontweight='bold')
fig.text(.02,.02,'Source: pinned supplied OpenFOAM case. Wall temperatures are simulated; this is not a fan performance test.',fontsize=9,color='#505861')
fig.tight_layout(rect=[0,.06,1,.92])
fig.savefig(out/'thermal_review.png',dpi=180)
print(out/'thermal_review.png')
