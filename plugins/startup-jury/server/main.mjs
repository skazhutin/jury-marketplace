import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import {StdioServerTransport} from '@modelcontextprotocol/sdk/server/stdio.js';
import {registerAppTool,registerAppResource,RESOURCE_MIME_TYPE} from '@modelcontextprotocol/ext-apps/server';
import {z} from 'zod';
import {spawn} from 'node:child_process';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const URI='ui://startup-jury/result-v1.html';
const version=JSON.parse(await readFile(path.join(ROOT,'package.json'),'utf8')).version;
const stateSchema={evaluation_id:z.string(),status:z.enum(['RUNNING','FINISHED','FAILED']),
  surface:z.literal('COMPUTER-ONLY'),synthetic:z.boolean(),started_at:z.number(),
  completed_roles:z.array(z.string()),started_roles:z.array(z.string()),finished_at:z.number().optional(),
  error:z.string().optional(),result:z.object({schema_version:z.literal(1),synthetic:z.boolean(),
    analysis_status:z.enum(['COMPLETE','LIMITED','BLOCKED']),verdict:z.enum(['PURSUE','VALIDATE FIRST','REFRAME','REJECT','NOT ISSUED']),
    confidence:z.enum(['LOW','MEDIUM','HIGH']),business_outcome:z.enum(['POTENTIAL VENTURE-SCALE COMPANY','POTENTIALLY STRONG BOOTSTRAPPED / NICHE BUSINESS','POSSIBLE SMALL BUSINESS','USEFUL PRODUCT, WEAK BUSINESS','NO CONVINCING BUSINESS MODEL','TOO EARLY TO CLASSIFY']),
    sections:z.record(z.string(),z.string()),experiments:z.array(z.object({fields:z.record(z.string(),z.string()),text:z.string()})),
    text_report:z.string(),limitations:z.array(z.string())}).optional()};
function adapter(operation,args){return new Promise((resolve,reject)=>{
  const script=operation==='health'?'doctor.py':'jobs.py';
  const child=spawn(process.env.STARTUP_JURY_PYTHON || 'python3',[path.join(ROOT,'scripts',script),...(operation==='health'?[]:[operation])],{cwd:ROOT,stdio:['pipe','pipe','ignore'],env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
  let data='';const timer=setTimeout(()=>child.kill(),60000);
  child.stdout.on('data',chunk=>{data+=chunk;if(data.length>12000000)child.kill();});
  child.on('error',()=>{clearTimeout(timer);reject(new Error('Local Python bridge could not start.'));});
  child.on('close',code=>{clearTimeout(timer);try{const out=JSON.parse(data);if(out.error && !out.status)reject(new Error(out.error));else if(code!==0 && !(operation==='health' && code===1 && out.status==='BLOCKED'))reject(new Error('Local bridge did not complete successfully.'));else resolve(out);}catch{reject(new Error('Local bridge returned an invalid response.'));}});
  child.stdin.end(JSON.stringify(args));
});}
function output(state){
  const copy=structuredClone(state);let details={};
  if(copy.result){
    const r=copy.result;details={reports:r.reports,claims:r.claims,sources:r.sources,runtime:r.runtime};
    delete r.reports;delete r.claims;delete r.sources;delete r.runtime;
  }
  let text=state.status==='FINISHED'?state.result.text_report:state.status==='FAILED'?`ANALYSIS STATUS: BLOCKED\nVERDICT: NOT ISSUED\n${state.error}`:`Startup Jury is running (${state.completed_roles.length}/11 reports captured). Retrieve evaluation ${state.evaluation_id} with get_evaluation; do not start another run.`;
  if(state.result?.limitations?.length)text+='\n\nExecution limitations:\n'+state.result.limitations.join('\n');
  return {structuredContent:copy,content:[{type:'text',text}],_meta:{startupJuryDetails:details},isError:state.status==='FAILED'};
}
async function call(operation,args){try{return output(await adapter(operation,args));}catch(error){return {isError:true,content:[{type:'text',text:error.message}]};}}
export function createServer(){
  const server=new McpServer({name:'startup-jury',version},{instructions:'Startup Jury uses the existing isolated eleven-role engine. Start once with a stable request_id, retrieve until terminal, then show_evaluation. Never substitute a model-authored verdict. synthetic_test runs only the fixed fictional regression packet. No external actions.'});
  server.registerTool('health_check',{title:'Check Startup Jury readiness',description:'Check bundled roles, runtime dependencies, compatible Codex and login without model calls or an evaluation. READY means local readiness; remote model access and a complete Jury run are checked during evaluation.',
    inputSchema:z.object({}).strict(),outputSchema:{plugin:z.string(),version:z.string(),status:z.enum(['READY','BLOCKED']),runtime_validation:z.string(),checks:z.array(z.object({name:z.string(),status:z.enum(['PASS','BLOCKED']),detail:z.string()}))},
    annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false,idempotentHint:true}},async()=>{try{const state=await adapter('health',{});return {structuredContent:state,content:[{type:'text',text:JSON.stringify(state)}],isError:state.status==='BLOCKED'};}catch(error){return {isError:true,content:[{type:'text',text:error.message}]};}});
  server.registerTool('start_evaluation',{title:'Evaluate a startup with Startup Jury',description:'Use this when the user invokes @Startup Jury or requests a Startup Jury evaluation. Submits the idea and permitted evidence to the EXISTING isolated eleven-role engine. Reuse request_id on retries. Use synthetic_test only for an explicitly requested installation regression; it ignores real startup input.',
    inputSchema:z.object({request:z.string().min(1).max(60000),request_id:z.string().regex(/^[A-Za-z0-9_-]{8,80}$/),synthetic_test:z.boolean().default(false)}).strict(),outputSchema:stateSchema,
    annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:true,idempotentHint:true}},args=>call('start',args));
  server.registerTool('get_evaluation',{title:'Retrieve Startup Jury progress or result',description:'Use this after start_evaluation. Wait up to 50 seconds for the same run; keep retrieving while RUNNING. Returns the exact Judge text without UI. Never starts another evaluation.',
    inputSchema:z.object({evaluation_id:z.string().regex(/^[0-9a-f]{32}$/),wait_seconds:z.number().int().min(0).max(50).default(0)}).strict(),outputSchema:stateSchema,
    annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false,idempotentHint:true}},args=>call('get',args));
  registerAppTool(server,'show_evaluation',{title:'Show Startup Jury decision',description:'Use this after an evaluation has started to display its compact result, evidence and original reports. Retrieve an existing evaluation only; no new evaluation or startup execution.',
    inputSchema:z.object({evaluation_id:z.string().regex(/^[0-9a-f]{32}$/)}).strict(),outputSchema:stateSchema,
    annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false,idempotentHint:true},
    _meta:{ui:{resourceUri:URI,visibility:['model','app']},'openai/outputTemplate':URI,'openai/widgetAccessible':true,
      'openai/toolInvocation/invoking':'Loading Startup Jury','openai/toolInvocation/invoked':'Startup Jury result'}},args=>call('get',args));
  registerAppResource(server,'Startup Jury decision',URI,{mimeType:RESOURCE_MIME_TYPE},async()=>({contents:[{uri:URI,mimeType:RESOURCE_MIME_TYPE,text:await readFile(path.join(ROOT,'web/result.html'),'utf8'),_meta:{ui:{prefersBorder:true,csp:{connectDomains:[],resourceDomains:[]}},'openai/widgetDescription':'Startup Jury verdict, decisive reasons, validation experiments and expandable original agent reports. Read-only.'}}]}));
  return server;
}
await createServer().connect(new StdioServerTransport());
