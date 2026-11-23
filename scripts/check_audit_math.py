import ast,hashlib,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'work/validation_audit_v2.py').read_text();tree=ast.parse(source);ns={'math':math}
module=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['primitive','exact']],type_ignores=[])
exec(compile(module,'audit_math','exec'),ns)
jobs=json.loads((root/'work/validation-review/manifest.json').read_text());settings={(j['voltage_v'],j['mobility'],j['injection']) for j in jobs if j['family']=='coaxial'};worst=0
for voltage,mu,rho in settings:
 ea,A,B,current,residual=ns['exact']({'voltage_v':voltage,'mobility':mu,'injection':rho});n=4096;h=math.log(100)/n
 def integrand(i):
  radius=.001*math.exp(i*h);return math.sqrt(A*radius*radius+B)
 integral=h/3*(integrand(0)+integrand(n)+sum((4 if i%2 else 2)*integrand(i) for i in range(1,n)))
 worst=max(worst,abs(integral-voltage)/voltage)
assert worst<1e-8
payload={'settings_checked':len(settings),'check':'closed-form voltage primitive checked against 4096-interval log-radius Simpson integration','worst_relative_voltage_difference':worst,'required_relative_agreement':1e-8,'analysis_script_sha256':hashlib.sha256(source.encode()).hexdigest()}
(root/'outputs/validation/audit_math_checks.json').write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps(payload))
