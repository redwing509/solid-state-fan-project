#!/usr/bin/env python3
"""Run one command and record a job manifest (stdlib only).

Usage:
  run_with_manifest.py --manifest M.json --case DIR [--log FILE ...] [--label TEXT] -- CMD [ARGS...]

The manifest records the command, working directory, case/log paths, host,
start and end timestamps (UTC), elapsed seconds, return code and a NaN/Inf
check over the logs and the latest time directory of the case. It is written
atomically before the run ("running") and again after it ("finished").
Exit status is the command's return code, or 3 when the command returned 0
but NaN/Inf values were found. Execution success is not validation.
"""
import argparse, json, math, os, re, socket, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

BAD = re.compile(r'(?<![A-Za-z_])(?:nan|-?inf(?:inity)?)(?![A-Za-z_])', re.I)
TIME_DIR = re.compile(r'^[0-9]+(?:\.[0-9]+)?(?:e[-+]?[0-9]+)?$')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def write(path, data):
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def scan(path, limit=20):
    hits, count = [], 0
    with open(path, errors='replace') as stream:
        for number, line in enumerate(stream, 1):
            if BAD.search(line):
                count += 1
                if len(hits) < limit:
                    hits.append({'line': number, 'text': line.strip()[:200]})
    return count, hits


def nan_check(case, logs):
    report = {'files_scanned': [], 'latest_time': None, 'nan_or_inf_found': False, 'hits': {}}
    targets = [Path(p) for p in logs if Path(p).is_file()]
    if case and case.is_dir():
        times = [d for d in case.iterdir() if d.is_dir() and TIME_DIR.match(d.name)]
        if times:
            latest = max(times, key=lambda d: float(d.name))
            report['latest_time'] = latest.name
            targets += sorted(f for f in latest.iterdir() if f.is_file() and f.stat().st_size < 512 * 2**20)
    for target in targets:
        count, hits = scan(target)
        report['files_scanned'].append(str(target))
        if count:
            report['nan_or_inf_found'] = True
            report['hits'][str(target)] = {'count': count, 'first': hits}
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--case')
    parser.add_argument('--log', action='append', default=[])
    parser.add_argument('--label', default='')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('missing command after --')
    manifest = Path(args.manifest).resolve()
    case = Path(args.case).resolve() if args.case else None
    record = {'schema': 'run-manifest/1', 'label': args.label, 'state': 'running',
              'command': command, 'cwd': os.getcwd(), 'host': socket.gethostname(),
              'case_path': str(case) if case else None, 'log_paths': [str(Path(p).resolve()) for p in args.log],
              'manifest_path': str(manifest), 'started_at_utc': now(), 'ended_at_utc': None,
              'elapsed_s': None, 'return_code': None, 'nan_check': None}
    write(manifest, record)
    start = time.monotonic()
    try:
        code = subprocess.call(command)
    except OSError as error:
        code, record['error'] = 127, str(error)
    record.update(state='finished', ended_at_utc=now(), elapsed_s=round(time.monotonic() - start, 3),
                  return_code=code, nan_check=nan_check(case, record['log_paths']))
    record['status'] = ('nan_or_inf' if record['nan_check']['nan_or_inf_found'] else
                        'ok' if code == 0 else 'failed')
    write(manifest, record)
    sys.exit(3 if code == 0 and record['status'] == 'nan_or_inf' else code)


if __name__ == '__main__':
    main()
