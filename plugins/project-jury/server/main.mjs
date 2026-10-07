// Transport adapted from the official Apps SDK low-level server example.
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema,ListToolsRequestSchema,ListResourcesRequestSchema,ReadResourceRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { root,engineRoot,resourceUri,packetFields,submit,retrieve,toolResult } from './adapter.mjs';

const version = JSON.parse(readFileSync(join(root,'package.json'),'utf8')).version;
const server = new Server({name:'project-jury',title:'Project Jury',version},{capabilities:{tools:{},resources:{}}});
const uiMeta = {ui:{resourceUri,visibility:['model','app']},'openai/outputTemplate':resourceUri,'openai/widgetAccessible':true,securitySchemes:[{type:'noauth'}]};
const tools = [
  {name:'health_check',title:'Check Project Jury readiness',description:'Check the bundled engine, native roles, Node/Python, compatible Codex and login without model calls or starting an evaluation. READY is local readiness; remote model access and a complete Jury run are checked during evaluation.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:false}},
  {name:'submit_evaluation',title:'Run Project Jury',description:'Use this when the user asks Project Jury to evaluate an idea. Submit the frozen PROJECT PACKET prepared with the bundled Project Jury packet and principles resources; do not improve the idea. Runs the existing isolated eight-agent engine on this computer. Generate one fresh UUID request_id, then retrieve that job until finished. For installation tests only, select synthetic_validation and omit packet/sources; it runs the existing synthetic fixture. Never evaluate or impersonate the reviewers in the parent conversation.',inputSchema:{type:'object',additionalProperties:false,properties:{request_id:{type:'string',format:'uuid'},mode:{type:'string',enum:['evaluation','synthetic_validation']},packet:{type:'object',description:'Exact neutral packet. Required fields: '+packetFields.join('; '),additionalProperties:true},common_sources:{type:'array',description:'Exact legitimately supplied source content/references, common to all first-stage roles. No unrelated local paths, secrets or coordinator opinions.',items:{}}},required:['request_id','mode']},annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:true},_meta:{...uiMeta,'openai/toolInvocation/invoking':'Starting independent Jury','openai/toolInvocation/invoked':'Jury started'}},
  {name:'get_result',title:'Read Project Jury result',description:'Use this to retrieve a previously submitted Project Jury job on this computer. Wait about 30 seconds between RUNNING responses. FINISHED returns the validated Judge report and result component. include_reports exposes only intentional role reports and permission evidence for text-only surfaces; it never exposes hidden reasoning or runtime traces.',inputSchema:{type:'object',additionalProperties:false,properties:{job_id:{type:'string',format:'uuid'},include_reports:{type:'boolean',default:false}},required:['job_id']},annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:false},_meta:{...uiMeta,'openai/toolInvocation/invoking':'Reading Jury result','openai/toolInvocation/invoked':'Jury result'}}
];
const refs = {'jury://instructions/packet':'project-packet.md','jury://instructions/principles':'principles-and-evidence.md'};
server.setRequestHandler(ListToolsRequestSchema,async()=>({tools}));
server.setRequestHandler(CallToolRequestSchema,async req=>{
  try {
    const args=req.params.arguments || {};
    if(req.params.name==='health_check'){
      if(Object.keys(args).length) throw new Error('Health check accepts no arguments.');
      const probe=spawnSync(process.env.PROJECT_JURY_PYTHON || 'python3',[join(root,'scripts/doctor.py')],{encoding:'utf8',timeout:45000,shell:false});
      if(probe.error || ![0,1].includes(probe.status)) throw new Error('Local readiness check could not complete.');
      const health=JSON.parse(probe.stdout);
      return {content:[{type:'text',text:JSON.stringify(health)}],structuredContent:health,isError:health.status==='BLOCKED'};
    }
    if(req.params.name==='submit_evaluation')return toolResult(submit(args));
    if(req.params.name==='get_result'){
      if(Object.keys(args).some(k=>!['job_id','include_reports'].includes(k)) || (args.include_reports!==undefined && typeof args.include_reports!=='boolean')) throw new Error('Unsupported result argument.');
      return toolResult(retrieve(args.job_id),args.include_reports);
    }
    throw new Error('Unknown Project Jury tool.');
  } catch(error) {return {isError:true,content:[{type:'text',text:error.message}]};}
});
server.setRequestHandler(ListResourcesRequestSchema,async()=>({resources:[{uri:resourceUri,name:'Project Jury result',mimeType:'text/html;profile=mcp-app'},...Object.keys(refs).map(uri=>({uri,name:refs[uri],mimeType:'text/markdown'}))]}));
server.setRequestHandler(ReadResourceRequestSchema,async req=>{
  const uri=req.params.uri;
  if(uri===resourceUri)return {contents:[{uri,mimeType:'text/html;profile=mcp-app',text:readFileSync(join(root,'ui/result.html'),'utf8'),_meta:{ui:{prefersBorder:true,csp:{connectDomains:[],resourceDomains:[]}},'openai/widgetDescription':'Project Jury verdict, decisive reasons, and inspectable intentional reviewer reports.','openai/widgetPrefersBorder':true,'openai/widgetCSP':{connect_domains:[],resource_domains:[]}}}]};
  if(Object.hasOwn(refs,uri))return {contents:[{uri,mimeType:'text/markdown',text:readFileSync(join(engineRoot,'references',refs[uri]),'utf8')}]};
  throw new Error('Unknown Project Jury resource.');
});
await server.connect(new StdioServerTransport());
