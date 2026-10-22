import csv
import json
from pathlib import Path
import re
import numpy as np
from scipy.integrate import quad, trapezoid
from scipy.optimize import brentq

root=Path('/opt/fan-research/2026-10-21/queue')
rows=[]
for job in json.loads((root/'manifest.json').read_text()):
    case=root/'cases'/job['id']; result_path=case/'result.json'
    if not result_path.exists():continue
    result=json.loads(result_path.read_text())
    row=dict(id=job['id'],family=job['family'],execution_status=result['status'],voltage_v=job['voltage_v'],scheme=job.get('scheme','upwind'),mesh_n=job.get('mesh_n'),elapsed_s=result.get('elapsed_s'))
    if job['family']=='coaxial' and result['status']=='executed':
        a,b,eps=1e-3,.1,8.854e-12
        mu,rho,v=job['mobility'],job['injection'],job['voltage_v']
        def ef(r,ea):
            ip=2*np.pi*a*mu*rho*ea
            return np.sqrt((a*ea/r)**2+ip/(2*np.pi*eps*mu)*(1-(a/r)**2))
        ea=brentq(lambda q:quad(lambda r:ef(r,q),a,b,epsabs=1e-6)[0]-v,1e3,1e8)
        exact_i=2*np.pi*a*mu*rho*ea
        patch=result['metrics']['last_patch_metrics']
        actual=patch['outer']['I']/(.01*.25)
        all_currents=[p.get('I',0.) for p in patch.values()]
        balance=abs(sum(all_currents))/max(sum(abs(q) for q in all_currents)*.5,1e-30)
        row.update(exact_current_a_per_m=exact_i,simulated_current_a_per_m=actual,current_relative_error=abs(actual-exact_i)/abs(exact_i),relative_discrete_charge_imbalance=balance)
        sampled=sorted((case/'postProcessing'/'sample').glob('*/ray45_V_rhoq_E_U.xy'),key=lambda p:float(p.parent.name))
        if sampled:
            dat=np.loadtxt(sampled[-1]); r=0.0011+dat[:,0]
            exact_e=ef(r,ea); e=np.linalg.norm(dat[:,3:6],axis=1)
            row['field_profile_relative_l2']=float(np.sqrt(trapezoid((e-exact_e)**2,r)/trapezoid(exact_e**2,r)))
            exact_rho=exact_i/(2*np.pi*mu*r*exact_e)
            row['charge_profile_relative_l2']=float(np.sqrt(trapezoid((dat[:,2]-exact_rho)**2,r)/trapezoid(exact_rho**2,r)))
            row['max_sampled_speed_m_s']=float(np.linalg.norm(dat[:,6:9],axis=1).max())
        row['validation_label']='REDUCED_ELECTRICAL_NUMERICAL_COMPARISON_NOT_FAN_VALIDATION'
    rows.append(row)
payload={'snapshot_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'completed_records':len(rows),'comparisons':rows}
(root/'comparison_snapshot.json').write_text(json.dumps(payload,indent=2))
if rows:
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with (root/'comparison_snapshot.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
print(json.dumps(payload,indent=2))
