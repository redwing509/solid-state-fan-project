import csv
import json
from pathlib import Path
import re
import sys
import numpy as np

case=Path(sys.argv[1])
out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)

def of_internal(path, count=4700):
    s=path.read_text()
    m=re.search(r'internalField\s+nonuniform\s+List<([^>]+)>\s+(\d+)\s*\(\s*(.*?)\s*\)\s*;',s,re.S)
    if m:
        a=np.fromstring(m[3].replace('(',' ').replace(')',' '),sep=' ')
        return a.reshape(int(m[2]),-1)
    m=re.search(r'internalField\s+uniform\s+([^;]+);',s)
    a=np.fromstring(m[1].replace('(',' ').replace(')',' '),sep=' ')
    return np.tile(a,(count,1))

def block(text,name):
    m=re.search(r'\b'+re.escape(name)+r'\s*\{',text)
    if not m: raise ValueError(name)
    level=1;i=m.end()
    for j in range(i,len(text)):
        level += (text[j]=='{')-(text[j]=='}')
        if not level:return text[i:j]
    raise ValueError('unbalanced dictionary')

def boundary_phi(name):
    text=block((case/'10'/'phi').read_text(),name)
    m=re.search(r'value\s+nonuniform\s+List<scalar>\s+\d+\s*\((.*?)\)\s*;',text,re.S)
    if m:return np.fromstring(m[1],sep=' ')
    m=re.search(r'value\s+uniform\s+([^;]+);',text)
    return np.array([float(m[1])]) if m else np.zeros(1)

def wall_vtk(path):
    tokens=path.read_text().split();i=tokens.index('POINTS');n=int(tokens[i+1]);i+=3
    points=np.array(tokens[i:i+3*n],dtype=float).reshape(-1,3)
    i=tokens.index('POLYGONS');n=int(tokens[i+1]);i+=3; polys=[]
    for _ in range(n):
        k=int(tokens[i]);i+=1;polys.append(np.array(tokens[i:i+k],dtype=int));i+=k
    i=tokens.index('FIELD')+3; fields={}
    while i<len(tokens):
        name=tokens[i];ncomp,ntuple=int(tokens[i+1]),int(tokens[i+2]);i+=4
        fields[name]=np.array(tokens[i:i+ncomp*ntuple],dtype=float).reshape(ntuple,ncomp);i+=ncomp*ntuple
    centres=np.array([points[p].mean(axis=0) for p in polys])
    areas=[]
    for p in polys:
        verts=points[p]; areas.append(np.linalg.norm(np.cross(verts,np.roll(verts,-1,axis=0)).sum(axis=0)*.5))
    return centres,np.array(areas),fields

summary={'execution':{'end_time_s':10,'exit_code':int((case/'continuation.exit').read_text()),'normal_end':bool(re.search(r'\nEnd\s*$',(case/'log.continuation').read_text()))},'fields':{},'last_interval_changes':{}}
for field in ['T','U','elecPot','chargeDens','elec','curDens']:
    a=of_internal(case/'10'/field); b=of_internal(case/'9.5'/field)
    mag=np.linalg.norm(a,axis=1) if a.shape[1]>1 else a[:,0]
    base=a-300 if field=='T' else a
    summary['fields'][field]={'finite':bool(np.isfinite(a).all()),'min':float(mag.min()),'max':float(mag.max()),'cell_count':len(a)}
    summary['last_interval_changes'][field]={'rms_absolute':float(np.sqrt(np.mean((a-b)**2))),'relative_l2':float(np.linalg.norm(a-b)/max(np.linalg.norm(base),1e-30)),'reference':'temperature rise from initial 300 K' if field=='T' else 'field norm','interval_s':[9.5,10]}
flux={p:float(boundary_phi(p).sum()) for p in ['left','right','down','up','hole']}
outward=sum(max(x,0) for x in flux.values()); net=sum(flux.values())
summary['volume_flux']={'patch_m3_s_outward_positive':flux,'net_m3_s':net,'relative_imbalance':abs(net)/max(outward,1e-30),'note':'Open benchmark boundaries, not delivered fan flow; stored phi includes 0.3 m extruded half-domain thickness'}
log=(case/'log.continuation').read_text()
cts=re.findall(r'time step continuity errors : sum local = ([^,]+), global = ([^,]+), cumulative = ([^\s]+)',log)
summary['final_logged_continuity']={'local':float(cts[-1][0]),'global':float(cts[-1][1]),'cumulative':float(cts[-1][2])}
rho,cp,nu,pr,kf,grad=1.225,1000.,1e-5,.9,.02,9350.
keff=rho*cp*nu/pr
summary['thermal_audit']={'rho_kg_m3':rho,'cp_j_kg_k':cp,'nu_m2_s':nu,'Pr':pr,'declared_but_unused_kf_w_m_k':kf,'gradient_k_m':grad,'effective_conductivity_w_m_k':keff,'effective_heat_flux_w_m2':keff*grad,'nominal_reference_heat_flux_w_m2':kf*grad,'relative_heat_flux_difference':(keff/kf-1),'ambient_fixed_temperature_boundary':False,'experimental_validation_status':'NOT_ESTABLISHED_THERMAL_INPUT_MISMATCH'}
c,area,fields=wall_vtk(case/'VTK'/'down'/'down_10.vtk')
cprev,_,previous=wall_vtk(case/'VTK'/'down'/'down_9.5.vtk')
assert np.allclose(c,cprev)
tw=fields['T'][:,0];rise=tw-300
summary['heated_wall']={'area_m2':float(area.sum()),'min_temperature_k':float(tw.min()),'max_temperature_k':float(tw.max()),'area_weighted_temperature_k':float(np.sum(tw*area)/area.sum()),'effective_heat_input_w':float(area.sum()*keff*grad),'nominal_heat_input_w':float(area.sum()*kf*grad)}
with (out/'heated_wall_profile.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['x_m','temperature_10s_k','temperature_9_5s_k','h_apparent_using_127_w_m2','h_apparent_using_187_w_m2','face_area_m2'])
    for i in np.argsort(c[:,0]):w.writerow([c[i,0],tw[i],previous['T'][i,0],keff*grad/rise[i],kf*grad/rise[i],area[i]])
(out/'legacy_review.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
