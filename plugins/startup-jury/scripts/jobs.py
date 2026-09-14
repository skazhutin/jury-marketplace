"""Private local evaluation jobs; no user-selected commands, paths or tools."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import uuid
sys.dont_write_bytecode=True
ROOT=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'jury-marketplace/startup-jury/jobs'
ENGINE=Path(__file__).resolve().parents[1]/'engine/scripts/run.py'

def initialize():
    if ROOT.is_symlink(): raise ValueError('Unsafe job storage')
    ROOT.mkdir(mode=0o700,parents=True,exist_ok=True)
    if ROOT.stat().st_uid!=os.getuid() or ROOT.stat().st_mode & 0o077: raise ValueError('Job storage must be private')

def write(path,value):
    tmp=path.with_suffix('.pending')
    with tmp.open('w') as f: json.dump(value,f)
    tmp.chmod(0o600);tmp.replace(path)

def folder(job_id):
    if not re.fullmatch(r'[0-9a-f]{32}',job_id): raise ValueError('Invalid evaluation ID')
    path=ROOT/job_id
    if path.is_symlink() or not path.is_dir():raise ValueError('Evaluation not found on this computer')
    return path

def read(job_id):
    p=folder(job_id);state=json.loads((p/'state.json').read_text())
    if state['status']=='RUNNING':
        try:os.kill(state['pid'],0)
        except ProcessLookupError:
            state.update(status='FAILED',error='The local engine process stopped before returning a complete result.')
            write(p/'state.json',state)
    if state['status']=='FINISHED':state['result']=json.loads((p/'result.json').read_text())
    return state

def start(args):
    if set(args)-{'request','request_id','synthetic_test'}:raise ValueError('Unknown input fields')
    request=args.get('request','');key=args.get('request_id','');synthetic=args.get('synthetic_test',False)
    if not isinstance(request,str) or not 1<=len(request)<=60000:raise ValueError('Provide 1–60000 characters of startup idea and permitted evidence')
    if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,80}',key):raise ValueError('Provide a stable request ID of 8–80 letters, digits, underscores or hyphens')
    if not isinstance(synthetic,bool):raise ValueError('synthetic_test must be boolean')
    digest=hashlib.sha256(json.dumps([request,synthetic]).encode()).hexdigest()
    keyhash=hashlib.sha256(key.encode()).hexdigest()
    with (ROOT/'registry.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        registry_path=ROOT/'registry.json'
        registry=json.loads(registry_path.read_text()) if registry_path.exists() else {}
        if keyhash in registry:
            item=registry[keyhash]
            if item['digest']!=digest:raise ValueError('Request ID already belongs to different input; use a new ID')
            return read(item['id'])
        for entry in registry.values():
            if read(entry['id'])['status']=='RUNNING':raise ValueError('Another Startup Jury evaluation is running; retrieve that result before starting another')
        if not ENGINE.is_file():raise ValueError('The bundled Startup Jury engine is incomplete; reinstall this plugin')
        jid=uuid.uuid4().hex;p=ROOT/jid;p.mkdir(mode=0o700)
        write(p/'input.json',{'request':request,'synthetic_test':synthetic})
        state={'evaluation_id':jid,'status':'RUNNING','started_at':time.time(),'completed_roles':[],
               'started_roles':[],'surface':'COMPUTER-ONLY','synthetic':synthetic}
        # Worker waits for initial state to be published; it never receives an executable from the tool caller.
        process=subprocess.Popen([sys.executable,str(Path(__file__).with_name('worker.py')),jid],
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
            cwd=Path(__file__).resolve().parents[1],start_new_session=True,
            env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        state['pid']=process.pid;write(p/'state.json',state)
        registry[keyhash]={'id':jid,'digest':digest};write(registry_path,registry)
        return state

def main():
    os.umask(0o077);initialize()
    args=json.load(sys.stdin)
    if not isinstance(args,dict):raise ValueError('Input must be an object')
    if sys.argv[1]=='start':out=start(args)
    elif sys.argv[1]=='get':
        if set(args)-{'evaluation_id','wait_seconds'}:raise ValueError('Unknown input fields')
        delay=args.get('wait_seconds',0)
        if not isinstance(delay,int) or not 0<=delay<=50:raise ValueError('wait_seconds must be 0–50')
        deadline=time.monotonic()+delay
        while True:
            out=read(args.get('evaluation_id',''))
            if out['status']!='RUNNING' or time.monotonic()>=deadline:break
            time.sleep(min(1,max(0,deadline-time.monotonic())))
    else:raise ValueError('Unsupported adapter operation')
    out.pop('pid',None)
    print(json.dumps(out))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:
        print(json.dumps({'error':str(e) if isinstance(e,ValueError) else 'Local evaluation storage is unavailable.'}));sys.exit(1)
