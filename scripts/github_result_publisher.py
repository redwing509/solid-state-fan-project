"""Publish bounded, completed fan-research results to the authorized private repo.

No credentials are loaded here. Main configures the export checkout and deploy key.
"""
import argparse
import csv
import fcntl
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
import time
from datetime import datetime, timezone

ROOT = Path('/opt/fan-research/2026-10-21')
REPO = ROOT / 'github-export'
QUEUE = ROOT / 'queue'
STATE = QUEUE / 'github_sync_status.json'
LIMIT, PART = 2 * 1024 ** 3, 40 * 1024 ** 2
TERMINAL = {'executed', 'failed', 'timeout', 'interrupted_requires_review', 'invalid_job'}
SECRET = re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b|\bAKIA[A-Z0-9]{16}\b')
DENY = {'.git', '.github', '.ssh', '.fleet', '.env', 'credentials', 'credentials.local.txt',
        'id_rsa', 'id_ed25519', 'lnInclude', '__pycache__', 'node_modules'}
QUEUE_FILES = ('status.json', 'manifest.json', 'queue_parameters.json', 'preflight.json',
               'comparison_snapshot.json', 'comparison_snapshot.csv', 'analysis_status.json')


class SafeStop(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != ROOT.parent):
        raise SafeStop('Symlink destination refused')
    temporary = path.with_name(path.name + '.publisher-tmp')
    with temporary.open('wb') as stream:
        stream.write(data)
    os.replace(temporary, path)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def excluded(relative, source=False):
    for piece in relative.parts:
        lowered = piece.lower()
        if piece in DENY or lowered.startswith('.env.') or lowered.endswith(('.pem', '.key', '.p12', '.pfx')):
            return True
        if 'credential' in lowered or lowered.startswith('id_ed25519') or lowered.startswith('id_rsa'):
            return True
    if source and ('Make' in relative.parts and any(p.startswith('linux') for p in relative.parts)):
        return True
    return source and relative.suffix.lower() in ('.o', '.so', '.a', '.pyc', '.dep')


def files_under(directory, source=False):
    if directory.is_symlink():
        raise SafeStop('Symlink source refused')
    found = []
    for current, folders, files in os.walk(directory, followlinks=False):
        for name in sorted(folders + files):
            path = Path(current, name)
            relative = path.relative_to(directory)
            if excluded(relative, source):
                if name in folders:
                    folders.remove(name)
                continue
            if path.is_symlink():
                raise SafeStop('Symlink in export source refused')
            if path.is_file():
                found.append(path)
    return sorted(found)


def inspect(path):
    if path.stat().st_size <= 5 * 1024 ** 2:
        data = path.read_bytes()
        if SECRET.search(data):
            raise SafeStop('Credential-format match; export stopped for review')


def export_size():
    return sum(p.stat().st_size for p in files_under(REPO))


def copy_file(source, destination):
    if source.is_symlink():
        raise SafeStop('Symlink source refused')
    inspect(source)
    if destination.is_symlink() or any(p.is_symlink() for p in destination.parents):
        raise SafeStop('Symlink destination refused')
    if destination.exists() and sha(source) == sha(destination):
        return
    if export_size() + source.stat().st_size > LIMIT:
        raise SafeStop('Export limit of 2 GiB reached')
    # Streaming temporary copy; replace only after complete bytes are on disk.
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.publisher-tmp')
    with source.open('rb') as incoming, temporary.open('wb') as outgoing:
        shutil_copy(incoming, outgoing)
    os.replace(temporary, destination)


def shutil_copy(incoming, outgoing):
    for chunk in iter(lambda: incoming.read(1024 * 1024), b''):
        outgoing.write(chunk)


def archive(directory, name, registry):
    paths = files_under(directory)
    fingerprint = hashlib.sha256(json_bytes([
        [str(p.relative_to(directory)), p.stat().st_size, p.stat().st_mtime_ns]
        for p in paths])).hexdigest()
    previous = registry.get(name, {})
    if previous.get('fingerprint') == fingerprint and all((REPO / p).is_file() for p in previous.get('files', [])):
        return
    for path in paths:
        inspect(path)
    scratch = QUEUE / 'publisher-work'
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='archive-', dir=scratch) as temporary:
        packed = Path(temporary) / 'payload.tar.gz'
        with packed.open('wb') as raw:
            with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as tar:
                    for path in paths:
                        info = tar.gettarinfo(str(path), arcname=str(path.relative_to(directory)))
                        info.uid = info.gid = 0
                        info.uname = info.gname = ''
                        with path.open('rb') as stream:
                            tar.addfile(info, stream)
                        if raw.tell() > LIMIT:
                            raise SafeStop('Single archive exceeds export limit')
        if export_size() + packed.stat().st_size > LIMIT:
            raise SafeStop('Export limit of 2 GiB reached')
        records = []
        total_sha = sha(packed)
        with packed.open('rb') as stream:
            for index in range((packed.stat().st_size + PART - 1) // PART):
                suffix = '.tar.gz' if packed.stat().st_size <= PART else '.tar.gz.part%04d' % index
                relative = 'raw-cases/' + name + suffix
                data = stream.read(PART)
                atomic(REPO / relative, data)
                records.append({'path': relative, 'size_bytes': len(data),
                                'sha256': hashlib.sha256(data).hexdigest()})
        manifest = {'format': 'concatenate parts in listed order to restore exact tar.gz bytes',
                    'archive_sha256': total_sha, 'archive_size_bytes': packed.stat().st_size,
                    'source_file_count': len(paths), 'parts': records}
        atomic(REPO / 'raw-cases' / (name + '.manifest.json'), json_bytes(manifest))
        newfiles = [r['path'] for r in records]
        for stale in previous.get('files', []):
            if stale not in newfiles and re.fullmatch(r'raw-cases/[A-Za-z0-9_-]+\.tar\.gz(?:\.part\d{4})?', stale):
                target = REPO / stale
                if target.is_symlink():
                    raise SafeStop('Symlink stale archive refused')
                target.unlink(missing_ok=True)
        registry[name] = {'fingerprint': fingerprint, 'files': newfiles, 'archive_sha256': total_sha}


def git(*args, allowed=(0,)):
    result = subprocess.run(['git', '-C', str(REPO), *args], capture_output=True,
                            text=True, timeout=180)
    if result.returncode not in allowed:
        raise SafeStop('Git operation failed; retained local commit/files for retry')
    return result


def publish_git():
    if git('branch', '--show-current').stdout.strip() != 'main':
        raise SafeStop('Export checkout must be on main')
    remote = git('remote', 'get-url', 'origin').stdout.strip()
    if remote not in ('git@github.com:redwing509/solid-state-fan-project.git',
                      'https://github.com/redwing509/solid-state-fan-project.git',
                      'ssh://git@github.com/redwing509/solid-state-fan-project.git'):
        raise SafeStop('Unexpected export remote; push refused')
    tracking = git('rev-parse', '--verify', 'refs/remotes/origin/main', allowed=(0, 128))
    if tracking.returncode == 0:
        behind, ahead = map(int, git('rev-list', '--left-right', '--count', 'origin/main...HEAD').stdout.split())
        if behind:
            raise SafeStop('Export main diverged or is behind origin/main; manual review required')
    tracked = git('ls-files', '-z').stdout.split('\0')
    for relative in filter(None, tracked):
        if excluded(Path(relative)):
            raise SafeStop('Excluded path already tracked; manual review required')
    # Stage only inspected regular files; never scoop up excluded untracked data.
    safe_paths = [str(p.relative_to(REPO)) for p in files_under(REPO)
                  if not p.name.endswith('.publisher-tmp')]
    for offset in range(0, len(safe_paths), 100):
        git('add', '--', *safe_paths[offset:offset + 100])
    missing = [relative for relative in tracked if relative and not (REPO / relative).exists()]
    for offset in range(0, len(missing), 100):
        git('add', '-u', '--', *missing[offset:offset + 100])
    changes = git('diff', '--cached', '--quiet', allowed=(0, 1)).returncode
    if changes:
        git('commit', '-m', 'Publish completed fan research results ' + now())
    # Always attempt push, even if no file changed: retries unpublished commits.
    git('push', 'origin', 'main')
    return git('rev-parse', 'HEAD').stdout.strip()


def snapshot(state):
    registry = state.setdefault('archives', {})
    published = []
    seed = ROOT / 'github-seed'
    if seed.is_dir():
        for path in files_under(seed):
            copy_file(path, REPO / path.relative_to(seed))
    cases = QUEUE / 'cases'
    if cases.is_dir():
        for case in sorted(cases.iterdir()):
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', case.name):
                continue
            if case.is_symlink():
                raise SafeStop('Symlink case refused')
            result = case / 'result.json'
            if not case.is_dir() or not result.is_file():
                continue
            record = json.loads(result.read_text())
            if record.get('status') not in TERMINAL:
                continue
            archive(case, case.name, registry)
            for name in ('result.json', 'job.json'):
                if (case / name).is_file():
                    copy_file(case / name, REPO / 'results' / case.name / name)
            published.append(case.name)
    baseline = ROOT / 'benchmark-case'
    if baseline.is_dir():
        archive(baseline, 'baseline', registry)
    for folder, label in ((ROOT / 'legacy-ehd', 'legacy-ehd'),
                          (ROOT / 'modern-ehd/source', 'modern-ehd')):
        if folder.is_dir() and not state.get('sources_seeded', {}).get(label):
            for path in files_under(folder, source=True):
                with path.open('rb') as header:
                    if header.read(4) == b'\x7fELF':
                        continue
                copy_file(path, REPO / 'pinned_public_source' / label / path.relative_to(folder))
            revision = subprocess.run(['git', '-C', str(folder), 'rev-parse', 'HEAD'],
                                      capture_output=True, text=True, timeout=30)
            if revision.returncode != 0 or not re.fullmatch(r'[a-f0-9]{40,64}\s*', revision.stdout):
                raise SafeStop('Cannot establish pinned public source revision')
            atomic(REPO / 'pinned_public_source' / label / 'UPSTREAM_REVISION.txt', revision.stdout.encode())
            state.setdefault('sources_seeded', {})[label] = revision.stdout.strip()
    for name in QUEUE_FILES:
        if (QUEUE / name).is_file():
            copy_file(QUEUE / name, REPO / 'results/queue' / name)
    manifest = []
    for path in files_under(REPO):
        if path.name == 'content-manifest.json' or path.name.endswith('.publisher-tmp'):
            continue
        inspect(path)
        manifest.append({'path': str(path.relative_to(REPO)), 'size_bytes': path.stat().st_size, 'sha256': sha(path)})
    atomic(REPO / 'content-manifest.json', json_bytes(manifest))
    if export_size() > LIMIT:
        raise SafeStop('Export limit of 2 GiB reached')
    state['exported_cases'] = published
    return published


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--oneshot-build-only', '--build-only', dest='oneshot_build_only',
                        action='store_true', help='Build exports without git mutation or network')
    args = parser.parse_args()
    QUEUE.mkdir(parents=True, exist_ok=True)
    if not REPO.is_dir() or REPO.is_symlink():
        raise SystemExit('Main must create a regular github-export checkout first')
    with (QUEUE / 'github_publisher.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('Another publisher holds the lock')
        state = json.loads(STATE.read_text()) if STATE.is_file() else {}
        final_refreshes = 0
        while True:
            state.update(updated_at=now(), state='building', publisher_pid=os.getpid(),
                         loop_interval_s=300, mode='build_only' if args.oneshot_build_only else ('once' if args.once else 'continuous'))
            atomic(STATE, json_bytes(state))
            try:
                snapshot(state)
                if args.oneshot_build_only:
                    state.update(state='build_only', updated_at=now())
                else:
                    commit = publish_git()
                    state.update(state='synced', updated_at=now(), latest_pushed_commit=commit,
                                 last_successful_push_at=now(), safe_error=None)
                status = json.loads((QUEUE / 'status.json').read_text()) if (QUEUE / 'status.json').is_file() else {}
                manifest = json.loads((QUEUE / 'manifest.json').read_text())
                jobs = manifest if isinstance(manifest, list) else manifest['jobs']
                complete = status.get('state') == 'finished' and all(job['id'] in state.get('exported_cases', []) for job in jobs)
                final_refreshes = final_refreshes + 1 if complete and state['state'] == 'synced' else 0
                state['final_synced_refreshes'] = final_refreshes
                if final_refreshes >= 3:
                    state['state'] = 'complete'
            except Exception as error:
                # Never write arbitrary git/SSH stderr, URLs with credentials or exception values.
                fatal = isinstance(error, SafeStop) and not str(error).startswith('Git operation failed;')
                state.update(state='stopped' if fatal else 'retry_pending',
                             updated_at=now(), safe_error=str(error) if isinstance(error, SafeStop) else type(error).__name__)
            atomic(STATE, json_bytes(state))
            if args.once or args.oneshot_build_only or state['state'] in ('complete', 'stopped'):
                return
            time.sleep(300)


if __name__ == '__main__':
    main()
