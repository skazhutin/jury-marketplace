#!/usr/bin/env python3
"""Job transport only. All evaluation and completion validation live in run_jury.py."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

os.umask(0o077)
job = Path(sys.argv[1]).resolve()
request = json.loads((job / 'request.json').read_text())
home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
engine = Path(__file__).resolve().parents[1] / 'engine/scripts/run_jury.py'
started = time.time()

def save(value):
    temp = job / 'status.json.tmp'
    temp.write_text(json.dumps(value, ensure_ascii=False))
    temp.replace(job / 'status.json')

state = {'job_id': job.name, 'job_status': 'RUNNING', 'started_at': started,
         'synthetic': request['mode'] == 'synthetic_validation', 'pid': os.getpid(),
         'engine': str(engine)}
save(state)
try:
    if not engine.is_file():
        raise ValueError('Bundled Project Jury engine is incomplete; reinstall this plugin.')
    command = [sys.executable, str(engine), '--format', 'json']
    if state['synthetic']:
        command += ['--smoke-test', '--trace', str(job / 'synthetic-runtime.jsonl')]
    else:
        payload = {'packet': request['packet'], 'common_sources': request['common_sources']}
        (job / 'input.json').write_text(json.dumps(payload, ensure_ascii=False))
        command += ['--input', str(job / 'input.json')]
    state['engine_sha256'] = hashlib.sha256(engine.read_bytes()).hexdigest()
    state['launcher_arguments'] = command[2:]
    save(state)
    with (job / 'engine-result.json').open('w') as output, (job / 'engine-stderr.txt').open('w') as errors:
        # The existing launcher creates and enforces the read-only isolated runtime.
        process = subprocess.Popen(command, stdout=output, stderr=errors, cwd=job, env=os.environ.copy())
        state['launcher_pid'] = process.pid
        save(state)
        code = process.wait()
    state['launcher_exit_code'] = code
    stderr = (job / 'engine-stderr.txt').read_text()
    receipt = re.search(r'(codex-cli [^;\n]+); Project Jury packet sha256=([a-f0-9]{64})', stderr)
    if receipt:
        state['runtime_version'], state['packet_sha256'] = receipt.groups()
    if code not in (0, 3):
        # The full trace is never returned by the plugin API.
        safe_errors = [line for line in stderr.splitlines() if line.startswith(('BLOCKED:', 'FAILED:'))]
        raise ValueError(safe_errors[-1] if safe_errors else f'Isolated engine failed (exit {code}); no verdict was issued.')
    result = json.loads((job / 'engine-result.json').read_text())
    # Accept only the intentionally produced completion transport, never JSONL runtime events.
    if not isinstance(result, dict) or not isinstance(result.get('roles'), list) or not isinstance(result.get('final_report'), str):
        raise ValueError('Existing engine returned an invalid completion transport.')
    state.update(job_status='FINISHED', result=result, finished_at=time.time())
except Exception as error:
    state.update(job_status='FAILED', error=str(error), finished_at=time.time())
save(state)
