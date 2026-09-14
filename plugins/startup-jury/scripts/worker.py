"""Execute only the existing isolated launcher and capture its public reports."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
sys.dont_write_bytecode=True
from jobs import ROOT,ENGINE,folder,write,initialize
os.umask(0o077);initialize();p=folder(sys.argv[1])
for _ in range(100):
    if (p/'state.json').exists():break
    time.sleep(.05)
state=json.loads((p/'state.json').read_text());args=json.loads((p/'input.json').read_text())
command=[sys.executable,str(ENGINE),'--result-json','--progress-json']
if args['synthetic_test']:command+=['--smoke','--audit-jsonl',str(p/'synthetic-native-events.jsonl')]
child=None;timer=None
try:
    with (p/'engine.stderr').open('w') as errors:
        child=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors,
            text=True,cwd=ENGINE.parent.parent,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        def terminate(*_):
            if child.poll() is None:child.terminate()
        signal.signal(signal.SIGTERM,terminate)
        timer=threading.Timer(5400,terminate);timer.daemon=True;timer.start()
        child.stdin.write(args['request']);child.stdin.close();result=None
        for line in child.stdout:
            event=json.loads(line)
            if event.get('event')=='progress':
                state.update(completed_roles=event['completed_roles'],started_roles=event['started_roles']);write(p/'state.json',state)
            elif event.get('event')=='result':result=event['result']
        code=child.wait()
        if code or result is None:raise RuntimeError(f'Existing isolated engine did not return a validated result (exit {code}). Inspect the local engine log; no startup verdict was issued.')
        write(p/'result.json',result);state.update(status='FINISHED',finished_at=time.time());write(p/'state.json',state)
except Exception as e:
    if child and child.poll() is None:child.terminate();child.wait(timeout=30)
    state.update(status='FAILED',error=str(e) if isinstance(e,RuntimeError) else 'The local result adapter failed before completing the evaluation.',finished_at=time.time());write(p/'state.json',state)
finally:
    if timer:timer.cancel()
