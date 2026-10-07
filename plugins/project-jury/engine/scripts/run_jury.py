#!/usr/bin/env python3
"""Launch the installed native Project Jury in a restricted ephemeral Codex session."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import re
import signal
import tomllib
import shlex
from native_runtime import prepare_agents, validate_reference_report, agent_flags, resolve_codex
from runtime_progress import RunProgress

ROLES=['project_value','project_technical','project_landscape','project_execution','project_advocate','project_skeptic','project_verifier','project_judge']
STAGE_ONE=['BOTTOM LINE','STRONGEST FINDINGS','STRONGEST ARGUMENT AGAINST MY OWN CONCLUSION','DECISION-CRITICAL ASSUMPTIONS','RISKS / FLAWS','RESULT','CONFIDENCE']
VERIFIER=['VERIFIED DECISION-CRITICAL FACTS','DISPROVEN / WEAK CLAIMS','IMPORTANT UNKNOWNS','DISPUTES RESOLVED','DISPUTES STILL UNRESOLVED','SOURCE-DEPENDENCY / CORRELATED-EVIDENCE RISKS','VERIFICATION LIMITATIONS']
JUDGE=['ANALYSIS STATUS','VERDICT','CONFIDENCE','DECISIVE REASON','WHAT IS ACTUALLY STRONG','WHAT IS ACTUALLY WEAK','FATAL FLAWS','MAJOR CONCERNS','KEY UNPROVEN ASSUMPTIONS','AGENT DISAGREEMENTS','REAL-WORLD / EXISTING-SOLUTIONS CHECK','TECHNICAL REALITY CHECK','ADOPTION / USE REALITY','COMMERCIAL UPSIDE','WHAT WOULD CHANGE THE VERDICT','FINAL ASSESSMENT']

def canary_shell_command(path):
    # Shell builtins avoid false permission failures from a deliberately empty PATH.
    return "printf '%s' 'jury-canary' > " + shlex.quote(str(path))

def object_schema(properties):
    return {'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}

def result_schema():
    string={'type':'string'}
    role=object_schema({'role':{'type':'string','enum':ROLES},'native_agent_id':string,'status':{'type':'string','enum':['complete','failed','not_started']},'attempts':{'type':'integer'},'input_hash':string,'received_reports':{'type':'array','items':{'type':'string','enum':ROLES}},'sibling_report_visible_before_submission':{'type':'boolean'},'report':string,'failure':string})
    return object_schema({'analysis_status':{'type':'string','enum':['COMPLETE','LIMITED','BLOCKED']},'verdict':{'type':'string','enum':['BUILD','PROTOTYPE FIRST','REWORK','REJECT','NOT ISSUED']},'final_report':string,'roles':{'type':'array','items':role},'stage_sequence':{'type':'array','items':{'type':'string','enum':['permission_preflight','stage_1_complete','verification_complete','adjudication_complete']}},'limitations':{'type':'array','items':string},'canary_attempted':{'type':'boolean'},'canary_denied':{'type':'boolean'},'permission_evidence':string,'web_probe_succeeded':{'type':'boolean'}})

def require_headings(report, headings):
    present=[re.sub(r'\s+\([^\n]*\)$','',m.group(1).strip()) for m in re.finditer(r'^#{1,3} (.+)$',report,re.M)]
    if any(h not in present for h in headings): raise ValueError('Incomplete required report headings.')

def section_value(report,heading):
    match=re.search(r'^#{1,3} '+re.escape(heading)+r'(?: \(([^\n]*)\))?[ \t]*\n+([^\n]+)',report,re.M)
    if not match:return None
    enums={'ANALYSIS STATUS':['COMPLETE','LIMITED','BLOCKED'],'VERDICT':['BUILD','PROTOTYPE FIRST','REWORK','REJECT','NOT ISSUED'],'RESULT':['PASS','UNCERTAIN','FAIL'],'CONFIDENCE':['LOW','MEDIUM','HIGH']}
    body=match.group(2).strip().strip('`* ')
    # A repeated field label is presentation, not a different enum value.
    body=re.sub(r'^'+re.escape(heading)+r'\s*[:=]\s*','',body,flags=re.I).strip('`* ')
    for value in enums.get(heading,[]):
        if re.match(r'^'+re.escape(value)+r'(?:[`*]*\s*$|[`*]*\s+[—–:-]\s+|[`*]*[.;,:](?:\s+|$))',body):return value
    # Some valid reports place the enum in the heading and prose in its body.
    if match.group(1) in enums.get(heading,[]):return match.group(1)
    return body

def validate_result(result,digest,smoke):
    if not isinstance(result,dict) or set(result)!=set(result_schema()['properties']): raise ValueError('Missing structured Jury completion record.')
    roles=result['roles']
    if len(roles)!=8 or {r['role'] for r in roles}!=set(ROLES): raise ValueError('Missing/duplicate reviewer ledger entries.')
    by={r['role']:r for r in roles}
    completed=set()
    ids=[]
    for name in ROLES:
        r=by[name]
        if r['status']=='complete':
            if not r['native_agent_id'] or r['input_hash']!=digest or r['attempts'] not in [1,2]: raise ValueError('Invalid completed reviewer identity, packet receipt, or attempts.')
            ids.append(r['native_agent_id'])
            if name in ROLES[:6]:
                if r['received_reports'] or r['sibling_report_visible_before_submission']: raise ValueError('Contaminated Stage 1 context.')
                validate_reference_report(r['report'], Path(__file__).resolve().parents[1], name)
                require_headings(r['report'],STAGE_ONE)
                if section_value(r['report'],'RESULT') not in ['PASS','UNCERTAIN','FAIL']: raise ValueError('Invalid Stage 1 result.')
                if section_value(r['report'],'CONFIDENCE') not in ['LOW','MEDIUM','HIGH']: raise ValueError('Invalid Stage 1 confidence.')
            else:
                expected=completed if name==ROLES[-1] else completed.intersection(ROLES[:6])
                if set(r['received_reports'])!=expected: raise ValueError('Later-stage report handoff is incomplete.')
                validate_reference_report(r['report'], Path(__file__).resolve().parents[1], name)
                require_headings(r['report'],VERIFIER if name==ROLES[-2] else JUDGE)
            completed.add(name)
        elif r['status']=='failed':
            if not r['failure'] or r['attempts'] not in [1,2]: raise ValueError('Missing terminal failure evidence.')
        elif r['status']!='not_started': raise ValueError('Unknown reviewer state.')
    if len(ids)!=len(set(ids)): raise ValueError('Reviewer contexts were reused.')
    if by[ROLES[-2]]['status']=='complete' and any(by[n]['status'] not in ['complete','failed'] for n in ROLES[:6]): raise ValueError('Verifier crossed Stage 1 barrier.')
    if by[ROLES[-1]]['status']=='complete' and by[ROLES[-2]]['status'] not in ['complete','failed']: raise ValueError('Judge crossed verification barrier.')
    if result['analysis_status'] not in ['COMPLETE','LIMITED','BLOCKED'] or result['verdict'] not in ['BUILD','PROTOTYPE FIRST','REWORK','REJECT','NOT ISSUED']: raise ValueError('Invalid analysis status/verdict.')
    if (result['analysis_status']=='BLOCKED') != (result['verdict']=='NOT ISSUED'): raise ValueError('Invalid blocked verdict pairing.')
    if completed and (not result['canary_attempted'] or not result['canary_denied'] or not result['permission_evidence']): raise ValueError('Missing successful permission preflight before reviewer dispatch.')
    if result['analysis_status']!='BLOCKED':
        if by[ROLES[-1]]['status']!='complete': raise ValueError('No completed Judge.')
    if by[ROLES[-1]]['status']=='complete':
        require_headings(result['final_report'],JUDGE)
        if result['final_report']!=by[ROLES[-1]]['report']: raise ValueError('Final report differs from Judge report.')
        if section_value(result['final_report'],'ANALYSIS STATUS')!=result['analysis_status'] or section_value(result['final_report'],'VERDICT')!=result['verdict']: raise ValueError('Judge report disagrees with completion metadata.')
        if section_value(result['final_report'],'CONFIDENCE') not in ['LOW','MEDIUM','HIGH']: raise ValueError('Invalid Judge confidence.')
    if result['analysis_status']=='COMPLETE' and len(completed)!=8: raise ValueError('Missing roles cannot be silently declared complete.')
    if smoke:
        if result['analysis_status']!='BLOCKED' or result['verdict']!='NOT ISSUED' or section_value(result['final_report'],'CONFIDENCE')!='LOW': raise ValueError('Synthetic fixture must not receive a substantive verdict.')
        if len(completed)!=8: raise ValueError('Synthetic routing test did not complete all eight roles.')
        if not result['canary_attempted'] or not result['canary_denied'] or not result['permission_evidence']: raise ValueError('Missing observed denied canary probe.')
        if not result['web_probe_succeeded']: raise ValueError('Native web probe did not succeed.')
        aliases={'stage1':'stage_1_complete','stage2':'verification_complete','stage3':'adjudication_complete'}
        stages=[aliases.get(s,s) for s in result['stage_sequence'] if s!='permission_preflight']
        if stages!=['stage_1_complete','verification_complete','adjudication_complete']: raise ValueError('Invalid smoke-test stage ordering.')
        require_headings(result['final_report'],JUDGE)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--input',type=Path)
    mode.add_argument('--smoke-test',action='store_true')
    parser.add_argument('--format',choices=['text','json'],default='text',help='Return the validated completion record for adapters, or the Judge report.')
    parser.add_argument('--trace',type=Path,help='Optional coordinator-owned JSONL evidence file.')
    parser.add_argument('--progress',type=Path,help='Private allowlisted operational metadata; no runtime text.')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    codex_home=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
    try:
        binary, version = resolve_codex()
    except RuntimeError as error:
        raise SystemExit('BLOCKED: ' + str(error))
    profile=root/'runtime.toml'
    if not profile.is_file(): raise SystemExit('BLOCKED: missing Project Jury runtime profile.')
    runtime_config=tomllib.loads(profile.read_text())
    if runtime_config.get('sandbox_mode')!='read-only' or runtime_config.get('approval_policy')!='never': raise SystemExit('BLOCKED: Jury profile has broader permissions than allowed.')
    if args.smoke_test:
        payload={'packet':{
            'PROJECT TYPE':'synthetic orchestration fixture',
            'PRIMARY PURPOSE':'verify reviewer routing and context only',
            'INTENDED DELIVERABLE':'eight correctly routed test reports; no real project',
            'INTENDED USER / AUDIENCE / BENEFICIARY':'installation test harness',
            'WHAT WOULD COUNT AS SUCCESS':'six independent role reports, verifier, then judge, with correct handoffs',
            'TARGET ENVIRONMENT / PLATFORM':'local Codex synthetic fixture',
            'KNOWN TEAM / TIME / BUDGET / COMPUTE / HARDWARE / DATA / ACCESS':'no real project resources asserted',
            'USER-SUPPLIED EVIDENCE':[],
            'EXPLICIT ASSUMPTIONS':['This is not an idea to evaluate.'],
            'IMPORTANT UNKNOWNS':['All substantive project details intentionally absent.'],
            'NONCE':'JURY-SYNTHETIC-2026-09-14-FROZEN-8E1C'},'common_sources':[]}
    else:
        payload=json.loads(args.input.read_text())
        if set(payload)!={'packet','common_sources'} or not isinstance(payload['packet'],dict) or not isinstance(payload['common_sources'],list):
            raise SystemExit('Input must contain exactly packet (object) and common_sources (array).')
        required=['PROJECT TYPE','PRIMARY PURPOSE','INTENDED DELIVERABLE','INTENDED USER / AUDIENCE / BENEFICIARY','WHAT WOULD COUNT AS SUCCESS','TARGET ENVIRONMENT / PLATFORM','KNOWN TEAM / TIME / BUDGET / COMPUTE / HARDWARE / DATA / ACCESS','USER-SUPPLIED EVIDENCE','EXPLICIT ASSUMPTIONS','IMPORTANT UNKNOWNS']
        if any(k not in payload['packet'] for k in required):
            raise SystemExit('BLOCKED: packet lacks required normalized fields; consult references/project-packet.md.')
    frozen=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    digest=hashlib.sha256(frozen.encode()).hexdigest()
    instructions=f'''You are the ISOLATED_JURY_PARENT coordinator, not a specialist.
Read {root}/references/orchestration.md, {root}/references/principles-and-evidence.md, {root}/references/stage-one-report.md, {root}/references/verification.md and {root}/references/adjudication.md in full. This is already the isolated launcher; do not relaunch it or create nested CLI processes.
Explicitly use the installed native custom agents: project_value, project_technical, project_landscape, project_execution, project_advocate, project_skeptic, then project_verifier, then project_judge. Inspect the actual spawn tool schema and select each custom agent using the supported selector. If custom-role selection is unavailable, stop with BLOCKED/NOT ISSUED and explain that capability limitation; do not impersonate agents or spawn generic agents with only a role label.
Pass the exact FROZEN_INPUT string and SHA256 below directly to every Stage 1 agent with no parent-history fork. No coordinator opinion or earlier report may be included. Each agent must echo receipt of the SHA256, its role identity, and the received report names. Only Stage 2 and 3 may receive earlier reports. Do not write reports to shared files. Capture results in memory and confirm terminal completion before later batches/stages. Follow the runtime lifecycle in orchestration.md: hosted collaboration releases active-turn capacity on completion and local V2 can evict completed idle children; neither needs a close tool. Use an actual close/release tool only when exposed and required by that runtime. Never reactivate or reuse a completed child's context for another role or retry. Use six concurrent specialists if the effective cap allows; otherwise independent batches. All specialists must have effective read-only sandbox, no shell networking, and no apps/MCP/plugins/image-generation mutation access. Check this in the selected custom agent's actual runtime, rather than inferring it from generic spawn documentation. Custom files disable agents and multi_agent as a best-effort additional control. Recursion is forbidden by the role instructions; if collaboration tools remain exposed despite those settings, record this technical limitation and require no recursive calls. Mere exposure of collaboration tools is not by itself an evaluation blocker; any actual recursive dispatch is a protocol failure. Before passing project content, spawn one project_technical custom agent with no packet for a SYNTHETIC_SMOKE_TEST=true permission preflight, inspect its actual tools/context and authorized disposable canary result, capture it, and wait for confirmed terminal completion. Do not require an unavailable close tool; never resume this preflight child. This preflight is not a Stage 1 report and must never be passed to Stage 1 reviewers. If the child retains mutation access or its canary write succeeds, stop. Do not treat written defaults as proof of effective enforcement.
Use the stage barriers, complete report formats, one retry per failed role, claim registry, disagreements, and failure handling in the references. Maintain an explicit ledger. Give the verifier and judge full reports, not summaries. Return the Judge's final structure. Never evaluate an unrelated alternative. Keep operational coordination brief. Tell each Stage 1 role to use at most 500 words excluding reference receipts, the Verifier 800 words and the Judge 1000 words. Preserve all required headings, compact decision-critical claim records, primary-source links and experiment criteria within these budgets. Prioritize claims capable of changing the verdict and stop redundant research. These output budgets do not waive evidence, permission, independence or stage-barrier requirements. Never rephrase a captured report to meet a budget; enforce it when dispatching the fresh role.
Do not send messages outside the reviewer workflow, publish, install, mutate services, edit files, or execute project code. Use only native web search for external research. Read only the named Jury references and the legitimately supplied common sources. Do not inspect other sessions, secrets, or unrelated files. For every shell read, explicitly set login=false and avoid interactive shells to prevent user startup scripts attempting unrelated changes. Use /bin/cat for the named reference reads if the stripped shell PATH has no cat executable.
'''
    if args.smoke_test:
        instructions+='''
SYNTHETIC_SMOKE_TEST=true. This is an installation routing test, not a project evaluation. Give this flag to all eight roles. Every stage should use its required headings but only report routing facts; no substantive investigation. Each Stage 1 role: RESULT=UNCERTAIN, CONFIDENCE=LOW. Verifier validates handoff. Judge: BLOCKED/NOT ISSUED/LOW because the fixture intentionally omits a real idea. Return a compact machine-readable test ledger after the synthetic Judge report: each role identity, submitted input hash, report names received, sibling visibility, attempts, schema validity; then stage ordering and missing-context handling. Do not claim an unexecuted check passed.
For effective child sandbox validation, ask project_technical to report the permission context supplied by the runtime and make one harmless write attempt to the absolute CANARY path below, using shell without escalation. This synthetic-only probe is authorized; a failed write is the expected result. Do not write elsewhere. Other roles must not try writes. Confirm no mutation integrations are exposed to the child. Report retained collaboration tools accurately and prohibit their use. Ask project_landscape to perform one native web search for the public IANA example domains documentation and report whether search worked; this is a tool-access probe only. It must not evaluate a real project. No further browsing.
'''
    instructions+='''\nMandatory references are injected in each native custom role's developer context. Preserve each role's JURY_REFERENCE_RECEIPTS line verbatim; missing or stale receipts make completion invalid. Never direct a role to omit mandatory rules or receipts.\nCompletion transport: return exactly the JSON object required by --output-schema. final_report is the Judge's verbatim markdown (or a concise coordinator BLOCKED explanation if no Judge completed); roles includes all eight entries with full reports, native IDs, the exact supplied digest, and explicit failure evidence. List report names actually supplied, not merely those expected. received_reports is reserved for the eight named Jury role reports in ROLES; never include permission_preflight, canary checks, packet, source materials, claim registries, or failure-record labels in that array. Record permission-preflight material separately in permission_evidence and limitations; this does not remove that evidence from the Verifier or Judge context. For blocked pre-dispatch, use not_started, attempts=0, empty report/ID/hash. stage_sequence records only actual completed barriers. Permission evidence must describe an observed attempted-and-denied canary and actual child capabilities, never infer success from file absence. Every run, including a normal evaluation, requires the authorized synthetic-only permission preflight before project input, and its attempted/denied evidence must be recorded. Only web_probe_succeeded may be false in a normal run. Never place an infrastructure limitation in FATAL FLAWS as if it were a project flaw.\n'''
    instructions+='''\nAn exposed sandboxed file tool such as apply_patch is not itself proof of effective write access: distinguish tool presence from permissions. During the synthetic permission preflight, you may ask project_technical to attempt one additional apply_patch creation of CANARY_PATCH below (no other path) to establish whether that path is blocked. Both canaries must remain absent. Tell the preflight agent to distinguish a callable image-generation backend from an imagegen skill catalog entry, SKILL.md, image display helper or generatedImage rendering helper. Those guidance/rendering entries alone do not establish mutation capability and must not block the evaluation. If an actual callable image-generation integration remains exposed despite disabling, name its tool/schema and stop without invoking it. If no callable backend is present and both write probes are denied, continue after confirmed terminal preflight completion.\n'''
    with tempfile.TemporaryDirectory(prefix='project-jury-') as temp:
        prepare_agents(temp, root, root/'native_agents', ROLES)
        canary=Path(temp)/'write-must-be-denied'
        canary_patch=Path(temp)/'patch-must-be-denied'
        instructions+=f'\nCANARY={canary}\nCANARY_PATCH={canary_patch}\nCANARY_SHELL_COMMAND={json.dumps(canary_shell_command(canary))}\nFROZEN_INPUT_SHA256={digest}\nFROZEN_INPUT={frozen}\n'
        instructions+='\nFor the synthetic-only shell write probe, pass the exact CANARY_SHELL_COMMAND string to project_technical and require its execution with login=false. It uses only a shell builtin and redirection; do not substitute touch, python or another PATH-dependent executable. Command-not-found is not sandbox denial evidence. If a probe used the wrong executable and failed to launch, repeat only the authorized disposable probe with this exact builtin command before deciding whether the permission barrier passed. Do not pass project content until an actual attempted write is observed to be denied.\n'
        # Ignore the normal config only for this subprocess. Auth remains in CODEX_HOME.
        schema_path=Path(temp)/'result-schema.json';schema_path.write_text(json.dumps(result_schema()))
        command=[str(binary),'exec','--strict-config','--ignore-user-config','--ignore-rules','--ephemeral','--skip-git-repo-check','--sandbox','read-only']
        # Explicit overrides remain effective even on runtimes where ignore-user-config
        # also suppresses a named user profile. Never pass secret-bearing base config.
        def config_flags(table,prefix=''):
            for key,value in table.items():
                dotted=prefix+key
                if isinstance(value,dict):yield from config_flags(value,dotted+'.')
                else:
                    if not isinstance(value,(str,bool,int,list)):raise ValueError('Unsupported Jury runtime setting: '+dotted)
                    yield '-c';yield dotted+'='+json.dumps(value)
        command+=list(config_flags(runtime_config))
        command+=list(agent_flags(temp, ROLES))
        command+=['-C',temp,'--json','--output-schema',str(schema_path),'-']
        env={k:v for k,v in os.environ.items() if k in ['PATH','HOME','USER','LOGNAME','TMPDIR','LANG','LC_ALL','CODEX_HOME','SSL_CERT_FILE','SSL_CERT_DIR','JURY_CODEX_BINARY']}
        # Version and payload hash contain no project content.
        print(f'{version}; Project Jury packet sha256={digest}',file=sys.stderr,flush=True)
        trace=args.trace.open('w') if args.trace else None
        progress=RunProgress(args.progress) if args.progress else None
        process=None
        timer=None
        previous_sigterm=signal.getsignal(signal.SIGTERM)
        def handle_sigterm(signum,frame):
            raise SystemExit(128+signum)
        signal.signal(signal.SIGTERM,handle_sigterm)
        try:
            process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env,start_new_session=True)
            process.stdin.write(instructions);process.stdin.close()
            # Stream stderr independently to prevent a full pipe from stalling a run.
            import threading
            def drain_stderr():
                for line in process.stderr:
                    if trace:
                        trace.write(json.dumps({'launcher_stderr':line.rstrip()})+'\n');trace.flush()
            thread=threading.Thread(target=drain_stderr,daemon=True);thread.start()
            def stop_process_group():
                try: os.killpg(process.pid,signal.SIGTERM)
                except ProcessLookupError: pass
                # A descendant may retain stdout after its parent exits, so signal
                # the entire original group again, independently of poll().
                time.sleep(5)
                try: os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError: pass
            timer=threading.Timer(2400,stop_process_group);timer.daemon=True;timer.start()
            final=[]
            turn_completed=False
            for line in process.stdout:
                if trace: trace.write(line);trace.flush()
                try: event=json.loads(line)
                except json.JSONDecodeError: continue
                if progress: progress.update(event)
                if event.get('type')=='item.completed':
                    item=event.get('item',{})
                    if item.get('type')=='agent_message': final.append(item.get('text',''))
                if event.get('type') in ['error','turn.failed']: print(json.dumps(event),file=sys.stderr,flush=True)
                if event.get('type')=='turn.completed': turn_completed=True
            result=process.wait();timer.cancel();thread.join(timeout=2)
            if canary.exists() or canary_patch.exists():
                raise SystemExit('FAILED: effective child permissions allowed the synthetic canary write. Do not use this runtime for Jury evaluation.')
            if result: raise SystemExit(f'BLOCKED: isolated Codex exited {result}; no successful Jury run is claimed.')
            if not final or not turn_completed: raise SystemExit('BLOCKED: runtime returned no completed turn.')
            try:
                result_json=json.loads(final[-1])
                if args.progress and isinstance(result_json,dict) and set(result_json)==set(result_schema()['properties']):
                    # Intentional completion candidate only; never a runtime trace.
                    # It is private debugging evidence, not an accepted Jury result.
                    (args.progress.parent/'unvalidated-completion.json').write_text(json.dumps(result_json,ensure_ascii=False))
                validate_result(result_json,digest,args.smoke_test)
            except (ValueError,KeyError,TypeError) as error:
                raise SystemExit(f'BLOCKED: completion validation failed: {error}')
            print(json.dumps(result_json,ensure_ascii=False) if args.format=='json' else result_json['final_report'])
            if result_json['analysis_status']=='BLOCKED' and not args.smoke_test: raise SystemExit(3)
        finally:
            signal.signal(signal.SIGTERM,previous_sigterm)
            if timer: timer.cancel()
            if process is not None and process.poll() is None:
                try: os.killpg(process.pid,signal.SIGTERM)
                except ProcessLookupError: pass
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try: os.killpg(process.pid,signal.SIGKILL)
                    except ProcessLookupError: pass
                    process.wait()
            if trace: trace.close()

if __name__=='__main__': main()
