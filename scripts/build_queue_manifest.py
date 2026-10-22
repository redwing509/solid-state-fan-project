import hashlib
import itertools
import json
from pathlib import Path

out=Path('outputs/queue');out.mkdir(parents=True,exist_ok=True)
jobs=[]
for n,scheme,v,mob,rho in itertools.product([48,96,192],['upwind','linearUpwind'],[10000,20000,30000,40000],[1.5e-4,1.8e-4,2.3e-4],[.5e-5,1e-5,2e-5]):
    jobs.append(dict(family='coaxial',voltage_v=v,mobility=mob,injection=rho,mesh_n=n,scheme=scheme,electric_force=False,timeout_s=600,classification='FIXED_INJECTION_ELECTRICAL_BENCHMARK',supply_mapping_status='UNAVAILABLE_NO_CONVERTER_MODEL'))
for v,mob,rho,force in itertools.product([20000,30000,40000,45000,50000],[1.5e-4,1.8e-4,2.3e-4],[2.2325e-5,4.465e-5,8.93e-5],[False,True]):
    jobs.append(dict(family='esp',voltage_v=v,mobility=mob,injection=rho,scheme='upwind',electric_force=force,timeout_s=900,classification='FIXED_INJECTION_FLOW_SENSITIVITY_NOT_CALIBRATED_CORONA',supply_mapping_status='UNAVAILABLE_NO_CONVERTER_MODEL'))

thermal=[
    ('consistent_Pr',.6125,9350,False,1.743e-4,2),
    ('corrected_wall_flux',.9,187/(1.225*1000*1e-5/.9),False,1.743e-4,2),
    ('ambient_control',.9,9350,True,1.743e-4,2),
    ('consistent_Pr_ambient',.6125,9350,True,1.743e-4,2),
    ('corrected_wall_flux_ambient',.9,187/(1.225*1000*1e-5/.9),True,1.743e-4,2),
    ('zero_injection_original',.9,9350,False,0,2),
    ('consistent_Pr_ambient_zero_injection',.6125,9350,True,0,2),
    ('consistent_Pr_ambient_timestep',.6125,9350,True,1.743e-4,1),
]
for label,pr,gradient,ambient,injection,co in thermal:
    jobs.append(dict(family='legacy',label=label,voltage_v=7540,mobility=.00023,injection=injection,Pr=pr,gradient=gradient,ambient_fixed=ambient,maxCo=co,timeout_s=3600,classification='THERMAL_AND_BOUNDARY_CONTROL_NOT_EXPERIMENTALLY_VALIDATED',supply_mapping_status='UNAVAILABLE_NO_CONVERTER_MODEL'))

def order(j):
    if j['family']=='coaxial':
        ref=j['voltage_v']==30000 and j['mobility']==1.8e-4 and j['injection']==1e-5
        return (0 if ref else 2,j['mesh_n'],j['scheme'],j['voltage_v'],j['mobility'],j['injection'])
    if j['family']=='esp':
        ref=j['voltage_v']==45000 and j['mobility']==1.8e-4 and j['injection']==4.465e-5
        return (1 if ref else 3,j['voltage_v'],j['mobility'],j['injection'],j['electric_force'])
    return (4,thermal.index(next(t for t in thermal if t[0]==j['label'])))
jobs.sort(key=order)
for j in jobs:
    digest=hashlib.sha256(json.dumps(j,sort_keys=True).encode()).hexdigest()[:10]
    j['id']=f"{j['family']}-{digest}"
assert len(jobs)==314
assert len({j['id'] for j in jobs})==len(jobs)
(out/'manifest.json').write_text(json.dumps(jobs,indent=2))
meta=dict(total_jobs=len(jobs),families={name:sum(j['family']==name for j in jobs) for name in ['coaxial','esp','legacy']},max_concurrent_jobs=1,container_cpu_limit=2,container_memory_gib=4,queue_output_limit_gib=20,minimum_free_disk_gib=30,
    requested_ac_supply_voltages=[110,220,330,440],electrode_voltages_are_distinct=True,
    limits='No local GPU work; no paid compute; no metal-specific results without surface/onset models',
    estimate='Roughly overnight to one day if modern runs complete promptly; timeouts, numerical instability or slow cases may extend it. This is a planning range, not a promised finish time.',
    stop='Create queue/STOP on mail to stop before the next job. Current per-job timeout still applies.',
    progress='/opt/fan-research/2026-10-21/queue/status.json',
    manifest_sha256=hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest())
(out/'queue_parameters.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta,indent=2))
