"""Bounded single-container CFD queue. Linux host; no credentials or networking.

Execution success is not numerical/experimental validation. Run only on mail at
the fixed project root, after reviewing queue/manifest.json.
"""
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path('/opt/fan-research/2026-10-21')
QUEUE = ROOT / 'queue'
IMAGES = {
    'modern': 'opencfd/openfoam-dev@sha256:2b206bc51fd428996d0ebbe67d751cc8f7e8d86aa431a62e6b409a40a5f38483',
    'legacy': 'openfoam/openfoam4-paraview50@sha256:a9cde0fffd6dee35f1d6fac0494d8595850aa8063005997a75c8430666f6c230'}
CAPS = {'coaxial': 600, 'esp': 900, 'legacy': 3600}
TERMINAL = {'executed', 'failed', 'timeout', 'skipped_manifest_mismatch',
            'interrupted_requires_review', 'invalid_job'}
NUMBER = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic(path, data):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False), encoding='utf-8')
    os.replace(temporary, path)


def digest(job):
    return hashlib.sha256(json.dumps(job, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def masked(text):
    # Preserve indices while hiding comments and quoted strings from brace matching.
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"'
    return re.sub(pattern, lambda m: ' ' * len(m.group()), text)


def block_bounds(text, name, lo=0, hi=None):
    hi = len(text) if hi is None else hi
    clean = masked(text)
    found = re.search(r'(?<![\w])' + re.escape(name) + r'\s*\{', clean[lo:hi])
    if not found:
        raise ValueError('Missing dictionary block: ' + name)
    opening = lo + found.end() - 1
    depth = 1
    for index in range(opening + 1, hi):
        depth += (clean[index] == '{') - (clean[index] == '}')
        if depth == 0:
            return opening + 1, index
    raise ValueError('Unbalanced dictionary block: ' + name)


def boundary(path, patch, value=None, kind=None, gradient=None):
    text = path.read_text()
    outer = block_bounds(text, 'boundaryField')
    start, end = block_bounds(text, patch, *outer)
    section = text[start:end]
    if kind is not None:
        section = replace_scalar(section, 'type', kind)
    if value is not None:
        entry = 'value uniform ' + format(value, '.15g') + ';'
        section, count = re.subn(r'(?m)^\s*value\s+[^;]*;', '\n        ' + entry, section)
        if count == 0:
            section += '\n        ' + entry + '\n'
        elif count != 1:
            raise ValueError('Ambiguous boundary value')
    if gradient is not None:
        section = replace_scalar(section, 'gradient', 'uniform ' + format(gradient, '.15g'))
    path.write_text(text[:start] + section + text[end:])


def replace_scalar(text, key, replacement):
    # Includes optional dimensioned-name and dimensions; replace last scalar token.
    pattern = r'(?m)^(\s*' + re.escape(key) + r'\s+)([^;\n]*);'
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise ValueError('Expected exactly one scalar entry: ' + key)
    match = matches[0]
    content = match.group(2)
    if '[' in content:
        closing = content.index(']')
        replacement = content[:closing + 1] + ' ' + str(replacement)
    return text[:match.start()] + match.group(1) + str(replacement) + ';' + text[match.end():]


def scalar_file(path, key, value):
    path.write_text(replace_scalar(path.read_text(), key, value))


def finite(job, key, lower, upper):
    value = job[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(key + ' must be finite numeric')
    if not lower <= value <= upper:
        raise ValueError(key + ' outside bounded range')
    return value


def validate(job):
    if not isinstance(job, dict) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', str(job.get('id', ''))):
        raise ValueError('Invalid job id')
    if job.get('family') not in CAPS:
        raise ValueError('Invalid family')
    finite(job, 'voltage_v', 0, 100000)
    finite(job, 'mobility', 1e-8, .01)
    finite(job, 'injection', 0, 1)
    finite(job, 'timeout_s', 1, CAPS[job['family']])
    if job.get('scheme', 'upwind' if job['family'] == 'legacy' else None) not in ('upwind', 'linearUpwind'):
        raise ValueError('Invalid scheme')
    if not isinstance(job.get('electric_force', True if job['family'] == 'legacy' else None), bool):
        raise ValueError('electric_force must be boolean')
    if job['family'] == 'coaxial':
        n = finite(job, 'mesh_n', 16, 384)
        if int(n) != n:
            raise ValueError('mesh_n must be integer')
    if job['family'] == 'legacy':
        if not job.get('electric_force', True):
            raise ValueError('Legacy binary has no electric_force runtime switch')
        finite(job, 'Pr', .01, 100)
        finite(job, 'gradient', 0, 1e6)
        finite(job, 'maxCo', .01, 2)
        if not isinstance(job.get('ambient_fixed'), bool):
            raise ValueError('ambient_fixed must be boolean')


def prepare(job, case):
    legacy = job['family'] == 'legacy'
    source = (ROOT / 'legacy-ehd/validationCase' if legacy else
              ROOT / 'modern-ehd/source/examples' /
              ('coaxialCorona' if job['family'] == 'coaxial' else 'espWirePlate'))
    # Only input dictionaries; never copy previous times, processors, or logs.
    case.mkdir()
    atomic(case / 'job.json', {'hash': digest(job), 'job': job})
    for folder in (('0.orig', 'constant', 'system') if legacy else ('0', 'constant', 'system')):
        shutil.copytree(source / folder, case / folder, symlinks=False)
    initial = case / ('0.orig' if legacy else '0')
    boundary(initial / ('elecPot' if legacy else 'V'), 'hole' if legacy else 'wire', value=job['voltage_v'])
    boundary(initial / ('chargeDens' if legacy else 'rhoq'), 'hole' if legacy else 'wire', value=job['injection'])
    if legacy:
        scalar_file(case / 'constant/EHDproperties', 'mobil', job['mobility'])
        scalar_file(case / 'constant/transportProperties', 'Pr', job['Pr'])
        boundary(initial / 'T', 'down', gradient=job['gradient'])
        if job['ambient_fixed']:
            boundary(initial / 'T', 'up', value=300, kind='fixedValue')
        scalar_file(case / 'system/controlDict', 'maxCo', job['maxCo'])
        key, field = 'div(rhoFlux,chargeDens)', 'chargeDens'
    else:
        scalar_file(case / 'constant/electricProperties', 'muq', job['mobility'])
        scalar_file(case / 'constant/electricProperties', 'electricForce', 'on' if job['electric_force'] else 'off')
        key, field = 'div((phi+rhoqFlux),rhoq)', 'rhoq'
    scheme = 'Gauss upwind' if job.get('scheme', 'upwind') == 'upwind' else 'Gauss linearUpwind grad(' + field + ')'
    scalar_file(case / 'system/fvSchemes', key, scheme)
    if job['family'] == 'coaxial':
        path = case / 'system/blockMeshDict'
        replacement = '(%d %d 1)' % (job['mesh_n'], job['mesh_n'] * 60 // 96)
        text, count = re.subn(r'\(\s*96\s+60\s+1\s*\)', replacement, path.read_text())
        if count != 1:
            raise ValueError('Unexpected coaxial mesh layout')
        path.write_text(text)


INSIDE = r'''
family="$1"
casepath="$2"
if [ "$family" = legacy ]; then
    . /opt/openfoam4/etc/bashrc
    binary=/work/bin/buoyantBoussinesqPimpleEHDFoam
else
    envfile=
    for candidate in /usr/lib/openfoam/openfoam2412/etc/bashrc /opt/openfoam2412/etc/bashrc /opt/OpenFOAM/OpenFOAM-v2412/etc/bashrc; do
        if [ -f "$candidate" ]; then envfile="$candidate"; break; fi
    done
    [ -n "$envfile" ] || { echo 'Missing OpenFOAM v2412 environment'; exit 64; }
    . "$envfile"
    binary=/work/modern-ehd/bin/electrostaticSimpleFoam
fi
set -e
cd "$casepath"
test -x "$binary"
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1
if [ "$family" = legacy ]; then
    cp -r 0.orig 0
    setFields > log.setFields 2>&1
fi
"$binary" > log.run 2>&1
if [ "$family" != legacy ]; then
    postProcess -func sample -latestTime > log.sample 2>&1
fi
'''


def summarize(case):
    path = case / 'log.run'
    metrics = {'last_time': None, 'last_patch_metrics': {}, 'end_marker': False,
               'fatal_marker': False, 'validation_status': 'not_assessed'}
    if not path.exists():
        return metrics
    # Stream logs rather than loading a potentially large transient run.
    with path.open(errors='replace') as stream:
        for line in stream:
            match = re.match(r'Time\s*=\s*(' + NUMBER + ')', line)
            if match:
                metrics['last_time'] = float(match.group(1))
            if line.strip() == 'End':
                metrics['end_marker'] = True
            if 'FOAM FATAL' in line or re.search(r'\b(?:nan|inf)\b', line, re.I):
                metrics['fatal_marker'] = True
            patch = re.match(r'patch\s+([A-Za-z0-9_-]+)', line.strip())
            if patch:
                values = {}
                for key, raw in re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(' + NUMBER + ')', line):
                    value = float(raw)
                    if math.isfinite(value):
                        values[key] = value
                metrics['last_patch_metrics'][patch.group(1)] = values
    return metrics


def execute(job, case):
    family = job['family']
    name = 'fan-queue-' + job['id'].lower()
    args = ['docker', 'run', '--rm', '--pull=never', '--name', name,
            '--network', 'none', '--cpus', '2', '--memory', '4g', '--memory-swap', '4g',
            '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
            '--pids-limit', '256', '--user', '0:0',
            '--mount', 'type=bind,src=' + str(ROOT) + ',dst=/work',
            '--entrypoint', '/bin/bash', IMAGES['legacy' if family == 'legacy' else 'modern'],
            '-c', INSIDE, 'fan-queue-inside', family, '/work/queue/cases/' + job['id']]
    with (case / 'log.container').open('w') as output:
        process = subprocess.Popen(args, stdout=output, stderr=subprocess.STDOUT)
        try:
            try:
                code = process.wait(timeout=job['timeout_s'])
                status = 'executed' if code == 0 else 'failed'
            except subprocess.TimeoutExpired:
                status = 'timeout'
                subprocess.run(['docker', 'kill', name], stdout=output, stderr=subprocess.STDOUT, timeout=30)
                code = process.wait(timeout=30)
        finally:
            if process.poll() is None:
                # On interruption/error, never proceed while an owned container may run.
                cleanup = subprocess.run(['docker', 'rm', '-f', name], stdout=output,
                                         stderr=subprocess.STDOUT, timeout=30)
                process.kill()
                process.wait(timeout=30)
                if cleanup.returncode != 0:
                    raise SystemExit('Container cleanup uncertain; worker stopped for review')
    metrics = summarize(case)
    if status == 'executed' and (not metrics['end_marker'] or metrics['fatal_marker']):
        status = 'failed'
    return {'status': status, 'exit_code': code, 'metrics': metrics}


def queue_size():
    total = 0
    for directory, folders, files in os.walk(QUEUE, followlinks=False):
        folders[:] = [name for name in folders if not Path(directory, name).is_symlink()]
        for name in files:
            path = Path(directory, name)
            if not path.is_symlink():
                total += path.stat().st_size
    return total


def existing_verification():
    response = subprocess.run(['docker', 'ps', '-a', '--format', '{{.Names}}'],
                              capture_output=True, text=True, check=True, timeout=30)
    return 'fan-modern-verification-20261021' in response.stdout.splitlines()


def main():
    def terminate(signum, frame):
        raise KeyboardInterrupt('Worker interrupted by signal ' + str(signum))
    signal.signal(signal.SIGTERM, terminate)
    QUEUE.mkdir(parents=True, exist_ok=True)
    with (QUEUE / 'worker.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('Another queue worker holds the lock')
        manifest = json.loads((QUEUE / 'manifest.json').read_text())
        jobs = manifest if isinstance(manifest, list) else manifest['jobs']
        ids = [job.get('id') for job in jobs]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate job ids')
        cases = QUEUE / 'cases'
        cases.mkdir(exist_ok=True)
        progress = {'started_at': now(), 'updated_at': now(), 'state': 'starting',
                    'jobs': {}, 'paused_families': [], 'validation_status': 'not_assessed'}
        failures = {family: 0 for family in CAPS}

        def save(state, reason=None):
            progress.update(state=state, updated_at=now(), reason=reason)
            atomic(QUEUE / 'status.json', progress)

        if existing_verification():
            save('waiting', 'Existing fan-modern-verification-20261021 container must be absent')
            return
        for job in jobs:
            identifier = job.get('id', '')
            family = job.get('family', '')
            try:
                validate(job)
            except (ValueError, KeyError, TypeError) as error:
                progress['jobs'][str(identifier)] = {'status': 'invalid_job', 'error': str(error)}
                save('running')
                continue
            case = cases / identifier
            result_path = case / 'result.json'
            if case.exists():
                record_path = case / 'job.json'
                same = record_path.is_file() and json.loads(record_path.read_text()).get('hash') == digest(job)
                if not same:
                    result = {'status': 'skipped_manifest_mismatch'}
                elif result_path.is_file():
                    result = json.loads(result_path.read_text())
                else:
                    result = {'status': 'interrupted_requires_review'}
                progress['jobs'][identifier] = result
                if result['status'] in ('failed', 'timeout', 'interrupted_requires_review'):
                    failures[family] += 1
                elif result['status'] == 'executed':
                    failures[family] = 0
                save('running')
                continue
            if failures[family] >= 3:
                if family not in progress['paused_families']:
                    progress['paused_families'].append(family)
                progress['jobs'][identifier] = {'status': 'paused_family', 'reason': 'Three consecutive family failures'}
                save('running')
                continue
            if (QUEUE / 'STOP').exists():
                save('stopped', 'STOP file present; no new container started')
                return
            if shutil.disk_usage(ROOT).free < 30 * 1024 ** 3:
                save('stopped', 'Free disk below 30 GiB')
                return
            if queue_size() > 20 * 1024 ** 3:
                save('stopped', 'Queue output exceeds 20 GiB')
                return
            if existing_verification():
                save('waiting', 'Verification container appeared; no new queue container started')
                return
            progress['current_job'] = identifier
            progress['jobs'][identifier] = {'status': 'running', 'started_at': now(), 'job_hash': digest(job)}
            save('running')
            started = time.monotonic()
            try:
                prepare(job, case)
                result = execute(job, case)
            except Exception as error:
                result = {'status': 'failed', 'error': type(error).__name__ + ': ' + str(error)}
            result.update(job_hash=digest(job), finished_at=now(), elapsed_s=round(time.monotonic() - started, 3),
                          validation_status='not_assessed')
            if case.is_dir():
                atomic(result_path, result)
            progress['jobs'][identifier] = result
            failures[family] = 0 if result['status'] == 'executed' else failures[family] + 1
            save('running')
        progress.pop('current_job', None)
        save('finished_with_paused_families' if progress['paused_families'] else 'finished')


if __name__ == '__main__':
    main()
