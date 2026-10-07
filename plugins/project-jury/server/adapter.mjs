import { mkdirSync, readFileSync, writeFileSync, existsSync, lstatSync, renameSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';

export const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
export const engineRoot = join(root, 'engine');
export const jobsRoot = join(process.env.CODEX_HOME || join(homedir(), '.codex'), 'jury-marketplace', 'project-jury', 'jobs');
export const packetFields = ['PROJECT TYPE','PRIMARY PURPOSE','INTENDED DELIVERABLE','INTENDED USER / AUDIENCE / BENEFICIARY','WHAT WOULD COUNT AS SUCCESS','TARGET ENVIRONMENT / PLATFORM','KNOWN TEAM / TIME / BUDGET / COMPUTE / HARDWARE / DATA / ACCESS','USER-SUPPLIED EVIDENCE','EXPLICIT ASSUMPTIONS','IMPORTANT UNKNOWNS'];
export const resourceUri = 'ui://project-jury/result-v1.html';
const uuid = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
const knownSections = [
  ['DECISIVE REASON','Decisive reasons'], ['WHAT IS ACTUALLY STRONG','What is actually strong'],
  ['WHAT IS ACTUALLY WEAK','What is actually weak'], ['FATAL FLAWS','Fatal flaws'],
  ['MAJOR CONCERNS','Major concerns'], ['KEY UNPROVEN ASSUMPTIONS','Key unproven assumptions'],
  ['REAL-WORLD / EXISTING-SOLUTIONS CHECK','Existing-solutions / real-world check'],
  ['TECHNICAL REALITY CHECK','Technical reality check'], ['ADOPTION / USE REALITY','Adoption / use reality'],
  ['AGENT DISAGREEMENTS','Agent disagreements'], ['WHAT WOULD CHANGE THE VERDICT','What would change the verdict'],
  ['FINAL ASSESSMENT','Final assessment'], ['COMMERCIAL UPSIDE','Commercial upside']
];

export function sections(report) {
  const found = {};
  let heading;
  for (const line of report.split('\n')) {
    const match = /^#{1,3} (.+)$/.exec(line);
    const key = match?.[1].replace(/\s+\([^\n]*\)$/, '').trim();
    if (key && [...knownSections.map(([k]) => k), 'ANALYSIS STATUS','VERDICT','CONFIDENCE'].includes(key)) {
      heading = key; const enumValue = match[1].match(/\((LOW|MEDIUM|HIGH)\)$/)?.[1]; found[heading] = enumValue ? enumValue+'\n' : '';
    } else if (heading) found[heading] += `${line}\n`;
  }
  return found;
}

function jobPath(id) {
  if (typeof id !== 'string' || !uuid.test(id)) throw new Error('A valid Project Jury job UUID is required.');
  const path = join(jobsRoot, id.toLowerCase());
  if (existsSync(path) && (!lstatSync(path).isDirectory() || lstatSync(path).isSymbolicLink())) throw new Error('Invalid job directory.');
  return path;
}

export function validateSubmission(args) {
  if (!args || Object.keys(args).some(k => !['request_id','mode','packet','common_sources'].includes(k))) throw new Error('Unsupported evaluation argument.');
  jobPath(args.request_id);
  if (!['evaluation','synthetic_validation'].includes(args.mode)) throw new Error('Choose evaluation or synthetic_validation.');
  if (Buffer.byteLength(JSON.stringify(args)) > 150000) throw new Error('Input exceeds 150 KB. Include only decision-relevant supplied material.');
  if (args.mode === 'synthetic_validation') {
    if ((args.packet && Object.keys(args.packet).length) || (args.common_sources?.length)) throw new Error('Synthetic validation accepts no project content; it uses the existing engine fixture.');
  } else {
    if (!args.packet || typeof args.packet !== 'object' || Array.isArray(args.packet) || packetFields.some(k => !(k in args.packet))) throw new Error('The complete frozen PROJECT PACKET is required. Read the installed Project Jury packet instructions.');
    if (!Array.isArray(args.common_sources)) throw new Error('common_sources must be an array of permitted user-provided material.');
  }
  return {request_id: args.request_id.toLowerCase(), mode: args.mode, packet: args.packet || {}, common_sources: args.common_sources || []};
}

function requestFingerprint(args) {
  const canonical = value => value && typeof value === 'object' ? (Array.isArray(value) ? value.map(canonical) : Object.fromEntries(Object.keys(value).sort().map(k => [k, canonical(value[k])]))) : value;
  return createHash('sha256').update(JSON.stringify(canonical(args))).digest('hex');
}

export function submit(args) {
  args = validateSubmission(args);
  if (!existsSync(join(engineRoot,'scripts/run_jury.py'))) throw new Error('The bundled Project Jury engine is incomplete; reinstall this plugin.');
  mkdirSync(jobsRoot,{recursive:true,mode:0o700});
  const path = jobPath(args.request_id);
  const digest = requestFingerprint(args);
  try { mkdirSync(path,{mode:0o700}); }
  catch (error) {
    if (error.code !== 'EEXIST') throw error;
    const previous = JSON.parse(readFileSync(join(path,'request.json'),'utf8'));
    if (requestFingerprint(previous) !== digest) throw new Error('This request_id already belongs to a different frozen request. Use a new UUID.');
    return retrieve(args.request_id);
  }
  writeFileSync(join(path,'request.json'),JSON.stringify(args),{mode:0o600,flag:'wx'});
  writeFileSync(join(path,'status.json'),JSON.stringify({job_id:args.request_id,job_status:'RUNNING',synthetic:args.mode==='synthetic_validation',started_at:Date.now()/1000}),{mode:0o600,flag:'wx'});
  const allowed = ['PATH','HOME','USER','LOGNAME','TMPDIR','LANG','LC_ALL','CODEX_HOME','SSL_CERT_FILE','SSL_CERT_DIR','JURY_CODEX_BINARY'];
  const env = Object.fromEntries(allowed.filter(k => process.env[k]).map(k => [k,process.env[k]]));
  const worker = spawn(process.env.PROJECT_JURY_PYTHON || 'python3',[join(root,'scripts/worker.py'),path],{cwd:path,env,stdio:'ignore',detached:true,shell:false});
  worker.once('error',error => {
    const state = {job_id:args.request_id,job_status:'FAILED',synthetic:args.mode==='synthetic_validation',error:`Unable to start isolated engine adapter: ${error.code}`};
    const temp = join(path,'status.json.tmp');writeFileSync(temp,JSON.stringify(state),{mode:0o600});renameSync(temp,join(path,'status.json'));
  });
  worker.unref();
  return retrieve(args.request_id);
}

export function retrieve(id) {
  const path = jobPath(id);
  if (!existsSync(join(path,'status.json'))) throw new Error('Project Jury job was not found on this computer.');
  const state = JSON.parse(readFileSync(join(path,'status.json'),'utf8'));
  if (state.job_status === 'RUNNING' && (Date.now()/1000-state.started_at > 2500)) {
    return {...state,job_status:'FAILED',error:'The isolated run did not finish within its runtime deadline. No successful result is claimed.'};
  }
  return state;
}

export function toolResult(state, includeReports=false) {
  const result = state.result;
  const parsed = sections(result?.final_report || '');
  const confidence = parsed.CONFIDENCE?.replace(/[`*]/g,'').trim().replace(/^CONFIDENCE\s*[:=]\s*/i,'').match(/^(LOW|MEDIUM|HIGH)\b/)?.[1] || (state.job_status === 'FAILED' ? 'LOW' : 'NOT ISSUED');
  const summary = {
    title:'PROJECT JURY',job_id:state.job_id,job_status:state.job_status,synthetic:!!state.synthetic,
    analysis_status:result?.analysis_status || (state.job_status === 'FAILED' ? 'BLOCKED' : 'PENDING'),
    verdict:result?.verdict || 'NOT ISSUED',confidence,
    message:state.error || (state.job_status === 'RUNNING' ? 'The independent Jury is running. Retrieve this job again in about 30 seconds; do not submit a duplicate evaluation.' : ''),
    sections:knownSections.map(([key,title])=>({title,text:parsed[key]?.trim() || 'Not reported.'})),
    final_report:result?.final_report || '',limitations:result?.limitations || [],
    runtime:{engine:state.engine || join(engineRoot,'scripts/run_jury.py'),engine_sha256:state.engine_sha256 || '',version:state.runtime_version || '',packet_sha256:state.packet_sha256 || '',stage_sequence:result?.stage_sequence || [],revalidation:state.revalidation || null}
  };
  const detail = result ? {roles:result.roles,permission_evidence:result.permission_evidence,canary_attempted:result.canary_attempted,canary_denied:result.canary_denied,web_probe_succeeded:result.web_probe_succeeded} : {roles:[]};
  let text = result ? `# PROJECT JURY\n\n${result.final_report}` : `# PROJECT JURY\n\nJob: ${state.job_id}\nExecution: ${state.job_status}\nANALYSIS STATUS: ${summary.analysis_status}\nVERDICT: NOT ISSUED\nCONFIDENCE: ${confidence}\n\n${summary.message}`;
  if (includeReports && result) text += '\n\n# INTENTIONAL JURY REPORTS\n\n'+result.roles.map(r=>`## ${r.role}\n\n${r.report || r.failure || 'Not started.'}`).join('\n\n')+'\n\n# PERMISSION EVIDENCE\n\n'+result.permission_evidence;
  return {content:[{type:'text',text}],structuredContent:summary,_meta:{juryDetail:detail},isError:state.job_status==='FAILED'};
}
