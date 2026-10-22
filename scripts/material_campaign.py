import csv
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/work')
ROOT.mkdir(parents=True, exist_ok=True)
EPS0 = 8.8541878128e-12
AREA = 1e-4  # assumed 1 cm2 planar coupon
THICKNESS = 1e-3  # assumed 1 mm total; not a proposed insulation specification
FREQ = 60
MATERIALS = [
    dict(name='air_reference', er=1.0, source='Idealized reference: relative permittivity 1', condition='ideal approximation'),
    dict(name='PTFE', er=2.1, source='https://www.daikinchemicals.com/solutions/technical-challenges/electrical-properties.html', condition='representative low-frequency supplier value; not guaranteed'),
    dict(name='PEEK_450G', er=3.0, source='https://www.victrex.com/en/downloads/datasheets/victrex-peek-450g', condition='23 C, 50 Hz; held constant at 60 Hz as approximation'),
    dict(name='BOROFLOAT_33', er=4.6, source='https://www.schott.com/-/media/project/onex/products/b/borofloat/downloads/schott-borofloat-technical-data-sheet-english-26032019.pdf?rev=aa66d15af04a4ce7994f5e7699350364', condition='25 C, 1 MHz supplier value; held constant at 60 Hz: unvalidated frequency extrapolation'),
    dict(name='alumina_AD96', er=9.0, source='https://www2.coorstek.com/media/4235/advanced-alumina.pdf', condition='25 C, 1 MHz supplier table indexed by search; direct fetch failed; held constant at 60 Hz: unvalidated frequency extrapolation'),
]


def finite_volume(er1, er2, fraction, voltage, n):
    # Node-centred variable-permittivity Poisson equation; interfaces align
    # exactly with edges. With no free charge this 1D solution is piecewise linear.
    dx = THICKNESS / n
    eps = [EPS0 * (er1 if (j + .5) / n < fraction else er2) for j in range(n)]
    weights = [e / dx for e in eps]
    lo, diag, up, rhs = [], [], [], []
    for j in range(1, n):
        lo.append(-weights[j - 1] if j > 1 else 0.0)
        diag.append(weights[j - 1] + weights[j])
        up.append(-weights[j] if j < n - 1 else 0.0)
        rhs.append(weights[0] * voltage if j == 1 else 0.0)
    for j in range(1, n - 1):
        factor = lo[j] / diag[j - 1]
        diag[j] -= factor * up[j - 1]
        rhs[j] -= factor * rhs[j - 1]
    vals = [0.0] * (n - 1)
    vals[-1] = rhs[-1] / diag[-1]
    for j in range(n - 3, -1, -1):
        vals[j] = (rhs[j] - up[j] * vals[j + 1]) / diag[j]
    potential = [voltage] + vals + [0.0]
    field = [(potential[j] - potential[j + 1]) / dx for j in range(n)]
    charge = eps[0] * field[0] * AREA
    flux = [eps[j] * field[j] for j in range(n)]
    return potential[int(round(n * fraction))], charge / voltage, max(field), (max(flux) - min(flux)) / max(abs(x) for x in flux)


cases, netlist, vectors = [], ['Layered dielectric screening - ideal linear capacitors'], []
for voltage, first, second, fraction in itertools.product([110, 220, 330, 440], MATERIALS, MATERIALS, [.25, .5, .75]):
    index = len(cases)
    tag = f'{index:03d}'
    d1, d2 = THICKNESS * fraction, THICKNESS * (1 - fraction)
    c1, c2 = EPS0 * first['er'] * AREA / d1, EPS0 * second['er'] * AREA / d2
    ceq = 1 / (1 / c1 + 1 / c2)
    vmid = voltage * c1 / (c1 + c2)
    emax = max((voltage - vmid) / d1, vmid / d2)
    row = dict(case_id=f'DIEL-{tag}', supply_v_rms=voltage, frequency_hz=FREQ,
        material_1=first['name'], material_2=second['name'], fraction_1=fraction,
        total_thickness_m=THICKNESS, area_m2=AREA,
        analytical_capacitance_f=ceq, analytical_midpoint_v_rms=vmid,
        analytical_current_a_rms=2 * math.pi * FREQ * ceq * voltage,
        analytical_max_field_v_m_rms=emax, maximum_field_peak_v_m=math.sqrt(2) * emax,
        classification='REDUCED_DIELECTRIC_SCREEN_NOT_FAN_VALIDATION',
        property_frequency_extrapolated=any(m['name'] in ['BOROFLOAT_33','alumina_AD96'] for m in [first,second]))
    grid_errors = []
    for n in [20,40,80]:
        mid, cap, field, flux_spread = finite_volume(first['er'], second['er'], fraction, voltage, n)
        error = max(abs(mid / vmid - 1), abs(cap / ceq - 1), abs(field / emax - 1))
        row[f'fv_{n}_relative_error'] = error
        row[f'fv_{n}_flux_relative_spread'] = flux_spread
        grid_errors.append(error)
    row['fv_max_relative_error'] = max(grid_errors)
    cases.append(row)
    netlist.extend([f'V{tag} in{tag} 0 DC 0 AC {voltage}', f'Ctop{tag} in{tag} mid{tag} {c1:.17g}', f'Cbot{tag} mid{tag} 0 {c2:.17g}'])
    vectors.extend([f'cur{tag}',f'vm{tag}'])
netlist.extend(['.control','set wr_singlescale','set wr_vecnames','set numdgt=15','ac lin 1 60 60'])
for index in range(len(cases)):
    tag = f'{index:03d}'
    netlist.extend([f'let cur{tag} = imag(i(V{tag}))', f'let vm{tag} = mag(v(mid{tag}))'])
netlist.extend(['wrdata ngspice-results.txt ' + ' '.join(vectors), 'quit','.endc','.end'])
(ROOT/'material-screen.cir').write_text('\n'.join(netlist)+'\n')
run = subprocess.run(['ngspice','-b','material-screen.cir'], cwd=ROOT, capture_output=True, text=True, timeout=90)
(ROOT/'ngspice-run.log').write_text(run.stdout+'\n'+run.stderr)
if run.returncode:
    raise RuntimeError(f'ngspice failed: {run.returncode}; see ngspice-run.log')
lines = (ROOT/'ngspice-results.txt').read_text().splitlines()
values = [float(v) for v in lines[-1].split()]
if len(values) != 1+2*len(cases):
    raise RuntimeError(f'Unexpected output columns: {len(values)}')
for index,row in enumerate(cases):
    current,midpoint = abs(values[1+2*index]),values[2+2*index]
    row['ngspice_current_a_rms']=current
    row['ngspice_midpoint_v_rms']=midpoint
    row['ngspice_relative_error']=max(abs(current/row['analytical_current_a_rms']-1),abs(midpoint/row['analytical_midpoint_v_rms']-1))
    row['numerical_check_passed']=max(row['ngspice_relative_error'],row['fv_max_relative_error']) < 1e-7
with (ROOT/'dielectric_results.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(cases[0]));writer.writeheader();writer.writerows(cases)
summary=dict(parameter_cases=len(cases),cases_per_voltage={str(v):sum(r['supply_v_rms']==v for r in cases) for v in [110,220,330,440]},
    passed=sum(r['numerical_check_passed'] for r in cases), ngspice_version=subprocess.run(['ngspice','--version'],capture_output=True,text=True).stdout,
    max_ngspice_relative_error=max(r['ngspice_relative_error'] for r in cases),max_fv_relative_error=max(r['fv_max_relative_error'] for r in cases),
    maximum_peak_field_v_m=max(r['maximum_field_peak_v_m'] for r in cases),materials=MATERIALS,
    limitations=['Parameter-case count includes deliberately equivalent/reversed-layer and uniform-material controls; it is not a count of independent designs',
    'Ideal linear 1D dielectric coupons; no discharge, leakage, loss, breakdown, edges, voids, converter or airflow',
    'Nominal permittivity held constant across frequency and field; glass/alumina values measured at 1 MHz, not verified at 60 Hz',
    '20/40/80 grids are interface-aligned and exact for piecewise-linear potential; this is not convergence evidence for complex EHD geometry',
    'Agreement between capacitor circuit, finite-volume discretization and analytical formula is numerical verification only'])
(ROOT/'dielectric_summary.json').write_text(json.dumps(summary,indent=2))
electrodes=['tungsten','stainless_steel','nichrome','copper','aluminum','titanium']
with (ROOT/'material_campaign_register.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['candidate_id','supply_v_rms','emitter','collector','layer_1','layer_2','fraction_1','status','related_screen_case','missing_physics'])
    for j,(row,emitter,collector) in enumerate(itertools.product(cases,electrodes,electrodes)):
        writer.writerow([f'CAND-{j:05d}',row['supply_v_rms'],emitter,collector,row['material_1'],row['material_2'],row['fraction_1'],
        'REGISTERED_NOT_EHD_SIMULATED',row['case_id'],'material-specific charge injection/onset/surface/aging; converter and real geometry'])
print(json.dumps({k:v for k,v in summary.items() if k not in ['materials','ngspice_version','limitations']},indent=2))
if summary['passed'] != len(cases):
    raise SystemExit('Numerical discrepancy requires review')
