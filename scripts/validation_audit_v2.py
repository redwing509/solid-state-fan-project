"""Read-only numerical/data audit; writes only a new analysis report."""
import collections,hashlib,json,math,re
from pathlib import Path
ROOT=Path('/opt/fan-research/2026-10-21');Q=ROOT/'queue'
jobs=json.loads((Q/'manifest.json').read_text());old={x['id']:x for x in json.loads((Q/'comparison_snapshot.json').read_text())['comparisons']}
def block(s,name):
 m=re.search(r'\b'+re.escape(name)+r'\s*\{',s)
 if not m:raise ValueError('Missing block '+name)
 level=1
 for i in range(m.end(),len(s)):
  level+=(s[i]=='{')-(s[i]=='}')
  if not level:return s[m.end():i]
 raise ValueError('Unclosed block')
def vals(s,key,n=1):
 m=re.search(r'\b'+key+r'\s+nonuniform\s+List<[^>]+>\s+(\d+)\s*\((.*?)\)\s*;',s,re.S)
 if m:
  a=[float(x) for x in m[2].replace('(',' ').replace(')',' ').split()];count=int(m[1]);assert len(a)%count==0
  return a,count
 m=re.search(r'\b'+key+r'\s+uniform\s+([^;]+);',s)
 if not m:return None,0
 a=[float(x) for x in m[1].replace('(',' ').replace(')',' ').split()];return a*n,n
def patches(case):
 s=(case/'constant/polyMesh/boundary').read_text();out={}
 for name in re.findall(r'(?m)^\s*(\w+)\s*\n\s*\{',s):
  if name=='FoamFile':continue
  b=block(s,name);n=re.search(r'nFaces\s+(\d+)',b);start=re.search(r'startFace\s+(\d+)',b)
  if n and start:out[name]={'n':int(n[1]),'start':int(start[1]),'empty':bool(re.search(r'type\s+empty\s*;',b))}
 return out
def latest(case):return max((p for p in case.iterdir() if p.is_dir() and re.fullmatch(r'\d+(?:\.\d+)?',p.name)),key=lambda p:float(p.name))
def fluxes(case,time):
 s=(time/'phi').read_text();out={}
 for name,p in patches(case).items():
  if p['empty']:continue
  a,n=vals(block(s,name),'value',p['n'])
  # Symmetry patches omit a stored value and impose zero normal flux.
  if a is None:
   b=block((case/'constant/polyMesh/boundary').read_text(),name)
   if re.search(r'type\s+symmetry(?:Plane)?\s*;',b):a=[0.]
   else:raise ValueError('Unknown patch flux '+name)
  out[name]=sum(a)
 den=sum(abs(x) for x in out.values())*.5
 return {'patch_m3_s':out,'net_m3_s':sum(out.values()),'relative_imbalance':abs(sum(out.values()))/max(den,1e-30)}
def intern(path):
 a,n=vals(path.read_text(),'internalField');return a,n
def mesh_areas(case,name):
 def content(path):
  s=re.sub(r'/\*.*?\*/','',path.read_text(),flags=re.S);s=re.sub(r'//[^\n]*','',s);s=s[s.index('}')+1:]
  m=re.search(r'^\s*\d+\s*\((.*)\)\s*$',s,re.S);assert m
  return m[1]
 points=[tuple(map(float,m)) for m in re.findall(r'\(\s*([^()]+)\)',content(case/'constant/polyMesh/points')) for m in [m.split()]]
 faces=[list(map(int,m.split())) for m in re.findall(r'\d+\s*\(([^()]*)\)',content(case/'constant/polyMesh/faces'))]
 p=patches(case)[name];areas=[]
 for indices in faces[p['start']:p['start']+p['n']]:
  v=[points[i] for i in indices];c=[0.,0.,0.]
  for a,b in zip(v,v[1:]+v[:1]):
   c[0]+=a[1]*b[2]-a[2]*b[1];c[1]+=a[2]*b[0]-a[0]*b[2];c[2]+=a[0]*b[1]-a[1]*b[0]
  areas.append(math.sqrt(sum(x*x for x in c))*.5)
 return areas
def primitive(r,A,B):
 y=math.sqrt(max(0,A*r*r+B))
 if B>0:
  c=math.sqrt(B);return y+c*math.log(math.sqrt(A)*r/(c+y))
 if B<0:
  c=math.sqrt(-B);return y-c*math.atan(y/c)
 return y
def exact(j):
 a,b,eps=.001,.1,8.854e-12;rho=j['injection'];mu=j['mobility']
 def voltage(ea):
  A=a*rho*ea/eps;B=a*a*(ea*ea-A);return primitive(b,A,B)-primitive(a,A,B)
 low,high=1.,1e9
 for _ in range(80):
  mid=(low+high)/2
  if voltage(mid)>j['voltage_v']:high=mid
  else:low=mid
 ea=(low+high)/2;A=a*rho*ea/eps;B=a*a*(ea*ea-A)
 return ea,A,B,2*math.pi*a*mu*rho*ea,voltage(ea)-j['voltage_v']
def norm(x,y,r):
 top=sum((r[i+1]-r[i])*((x[i]-y[i])**2+(x[i+1]-y[i+1])**2)*.5 for i in range(len(r)-1))
 den=sum((r[i+1]-r[i])*(y[i]**2+y[i+1]**2)*.5 for i in range(len(r)-1))
 return math.sqrt(top/den)
out={'method':'independently coded closed-form voltage primitive + bisection; existing fields only; retrospective','electrical':[],'duct':[],'thermal':[],'errors':[]}
cache={}
for j in jobs:
 case=Q/'cases'/j['id']
 try:
  result=json.loads((case/'result.json').read_text());time=latest(case);row={'id':j['id'],'time':float(time.name),'status':result['status']}
  if j['family']=='coaxial':
   key=(j['voltage_v'],j['mobility'],j['injection'])
   if key not in cache:cache[key]=exact(j)
   ea,A,B,current,residual=cache[key];p=max((case/'postProcessing/sample').glob('*/ray45_V_rhoq_E_U.xy'),key=lambda p:float(p.parent.name))
   dat=[[float(x) for x in line.split()] for line in p.read_text().splitlines() if line.strip() and not line.startswith('#')]
   sample=(case/'system/sample').read_text();xyz=[float(x) for x in re.search(r'start\s*\(([^)]+)',sample)[1].split()];offset=math.hypot(xyz[0],xyz[1]);rad=[offset+x[0] for x in dat]
   field=[math.sqrt(A+B/(r*r)) for r in rad];charge=[current/(2*math.pi*j['mobility']*r*e) for r,e in zip(rad,field)]
   measured=[math.sqrt(sum(v*v for v in x[3:6])) for x in dat]
   row.update(exact_current_a_per_m=current,previous_exact_current_relative_difference=abs(current-old[j['id']]['exact_current_a_per_m'])/current,voltage_residual_v=residual,sample_start_radius_m=offset,field_relative_l2=norm(measured,field,rad),charge_relative_l2=norm([x[2] for x in dat],charge,rad),old_field_relative_l2=old[j['id']]['field_profile_relative_l2'],quarter_depth_factor_m=.25*.01)
   out['electrical'].append(row)
  elif j['family']=='esp':
   row.update(voltage_v=j['voltage_v'],mobility=j['mobility'],injection=j['injection'],electric_force=j['electric_force'],volume_flux=fluxes(case,time));a,n=intern(time/'U');row['max_cell_speed_m_s']=max(math.sqrt(sum(v*v for v in a[i:i+3])) for i in range(0,len(a),3))
   patch=result['metrics']['last_patch_metrics'];currents=[v.get('I',0.) for v in patch.values()];row['relative_patch_current_imbalance']=abs(sum(currents))/max(sum(abs(x) for x in currents)*.5,1e-30);out['duct'].append(row)
  else:
   a,n=intern(time/'T');area=mesh_areas(case,'down');tw,count=vals(block((time/'T').read_text(),'down'),'value',len(area));assert tw is None or len(tw)==len(area)
   alpha=1e-5/j['Pr'];k=1.225*1000*alpha;row.update(label=j['label'],Pr=j['Pr'],ambient_fixed=j['ambient_fixed'],maxCo=j['maxCo'],gradient_k_m=j['gradient'],laminar_effective_conductivity_w_m_k=k,laminar_imposed_heat_flux_w_m2=k*j['gradient'],heated_area_m2=sum(area),laminar_wall_heat_input_w=k*j['gradient']*sum(area),wall_area_weighted_temperature_k=None if tw is None else sum(x*y for x,y in zip(tw,area))/sum(area),internal_temperature_range_k=[min(a),max(a)],volume_flux=fluxes(case,time),transport_properties=(case/'constant/transportProperties').read_text(),turbulence_properties=(case/'constant/turbulenceProperties').read_text() if (case/'constant/turbulenceProperties').exists() else None)
   row['wall_temperature_note']='fixedGradient field does not store patch values; exact wall reconstruction pending' if tw is None else 'stored patch values'; row['alphat_internal_max_m2_s']=max(intern(time/'alphat')[0]) if (time/'alphat').exists() else None; out['thermal'].append(row)
 except Exception as e:out['errors'].append({'id':j['id'],'error':type(e).__name__+': '+str(e)})
(Q/'validation_audit_v2.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({'electrical':len(out['electrical']),'duct':len(out['duct']),'thermal':len(out['thermal']),'errors':out['errors'][:10],'reference_current_difference_max':max((x['previous_exact_current_relative_difference'] for x in out['electrical']),default=None)}))
