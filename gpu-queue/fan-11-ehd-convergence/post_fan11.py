#!/usr/bin/env python3
# Post-processing for fan-11 (python3.5 compatible: no f-strings, no numpy needed).
# Metrics at final time per case: heated-plate mean T (patch 'down', from patchAverage), max |U|, max T,
# max chargeDens; then Celik et al. (2008) GCI on M1/M2/M4 (r=2) and time-step sensitivity on M2.
import json, math, os, re, sys, glob
R = sys.argv[1]; cases = {}
def latest(d):
    ts = [x for x in os.listdir(d) if re.match(r'^[0-9.eE+-]+$', x) and x != '0']
    return max(ts, key=float) if ts else None
def internal(path, vector=False):
    s = open(path).read(); m = re.search(r'internalField\s+nonuniform\s+List<\w+>\s*\n?(\d+)\s*\(', s)
    if not m:
        m2 = re.search(r'internalField\s+uniform\s+([^;]+);', s); return None
    body = s[m.end():]; n = int(m.group(1))
    if vector:
        v = re.findall(r'\(([^()]+)\)', body)[:n]; return [math.sqrt(sum(float(c) ** 2 for c in t.split())) for t in v]
    return [float(x) for x in body.split(')')[0].split()[:n]]
for d in sorted(glob.glob(os.path.join(R, 'cases', '*'))):
    n = os.path.basename(d); st = open(os.path.join(d, 'run.status')).read() if os.path.exists(os.path.join(d, 'run.status')) else ''
    rec = {'status': st.strip()}; lt = latest(d); rec['final_time'] = lt
    m = re.search(r'cells (\d+)', st); rec['cells'] = int(m.group(1)) if m else None
    m = re.search(r'rc (\d+)', st); rec['rc'] = int(m.group(1)) if m else None
    if lt:
        try:
            rec['Umax'] = max(internal(os.path.join(d, lt, 'U'), True)); rec['Tmax'] = max(internal(os.path.join(d, lt, 'T')))
            rec['rho_q_max'] = max(internal(os.path.join(d, lt, 'chargeDens')))
            rec['nonfinite'] = any(not math.isfinite(x) for x in internal(os.path.join(d, lt, 'T')))
        except Exception as e:
            rec['field_error'] = str(e)
    pa = os.path.join(d, 'log.patchAverage')
    if os.path.exists(pa):
        m = re.findall(r'areaAverage\(down\) of T = ([-0-9.eE+]+)', open(pa).read())
        if m: rec['Tdown_mean'] = float(m[-1])
    cases[n] = rec
def gci(f1, f2, f3, r=2.0, Fs=1.25):
    e32, e21 = f3 - f2, f2 - f1
    if e21 == 0 or e32 == 0: return {'note': 'zero difference'}
    s = 1 if e32 / e21 > 0 else -1; p = abs(math.log(abs(e32 / e21))) / math.log(r)
    for _ in range(100):
        q = math.log((r ** p - s) / (r ** p - s)); p = abs(math.log(abs(e32 / e21)) + q) / math.log(r)
    ea = abs(e21 / f1); g = Fs * ea / (r ** p - 1) if r ** p > 1 else float('inf')
    return {'p': p, 'GCI_fine_pct': 100 * g, 'monotone': (e32 / e21) > 0, 'f_extrap': f1 + e21 / (r ** p - 1) if r ** p != 1 else None}
summ = {'cases': cases, 'gci': {}, 'dt': {}}
if all(k in cases for k in ('M1', 'M2', 'M4')):
    for q in ('Tdown_mean', 'Umax', 'Tmax'):
        try: summ['gci'][q] = gci(cases['M4'][q], cases['M2'][q], cases['M1'][q])
        except Exception as e: summ['gci'][q] = {'error': str(e)}
for q in ('Tdown_mean', 'Umax'):
    try:
        base = cases['M2'][q]; summ['dt'][q] = {k: 100 * (cases[k][q] - base) / base for k in ('M2-Co1', 'M2-Co05') if k in cases and q in cases[k]}
    except Exception as e: summ['dt'][q] = {'error': str(e)}
# verdicts per ACCEPTANCE_CRITERIA.md
v = {}
for q, lim in (('Tdown_mean', 2.0), ('Umax', 5.0)):
    g = summ['gci'].get(q, {})
    v[q] = 'PASS' if g.get('monotone') and 0.5 <= g.get('p', 0) <= 4 and g.get('GCI_fine_pct', 1e9) <= lim else 'NOT-PASSED'
dvals = [x for q in summ['dt'].values() if isinstance(q, dict) for x in q.values() if isinstance(x, float)]
v['time_step'] = 'PASS' if len(dvals) == 4 and all(abs(x) <= 1.0 for x in dvals) else 'NOT-PASSED'
summ['verdicts'] = v
json.dump(summ, open(os.path.join(R, 'summary.json'), 'w'), indent=2, sort_keys=True)
with open(os.path.join(R, 'summary.md'), 'w') as f:
    f.write('# fan-11 summary\n\n| case | cells | rc | final t | Tdown_mean | Umax | Tmax |\n|---|---|---|---|---|---|---|\n')
    for n, c in sorted(cases.items()):
        f.write('| %s | %s | %s | %s | %s | %s | %s |\n' % (n, c.get('cells'), c.get('rc'), c.get('final_time'), c.get('Tdown_mean'), c.get('Umax'), c.get('Tmax')))
    f.write('\nGCI: %s\n\ndt sensitivity (%% vs M2): %s\n\nverdicts: %s\n' % (json.dumps(summ['gci']), json.dumps(summ['dt']), json.dumps(v)))
print('verdicts', json.dumps(v))
