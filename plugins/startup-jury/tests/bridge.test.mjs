import test from 'node:test';
import assert from 'node:assert/strict';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
const testHome=fs.mkdtempSync(os.tmpdir()+'/startup-jury-contract-');
process.env.CODEX_HOME=testHome;
test.after(()=>fs.rmSync(testHome,{recursive:true,force:true}));
const root=new URL('../',import.meta.url).pathname;
test('installed-format bridge exposes only bounded evaluation tools and inert UI',async()=>{
 const client=new Client({name:'startup-jury-contract-test',version:'1.0.0'});
 await client.connect(new StdioClientTransport({command:'python3',args:[root+'scripts/start_server.py'],cwd:root,stderr:'pipe',env:{...process.env,JURY_CODEX_BINARY:'/missing-jury-test-runtime'}}));
 try{
  const {tools}=await client.listTools();assert.deepEqual(tools.map(t=>t.name).sort(),['get_evaluation','health_check','show_evaluation','start_evaluation']);
  for(const t of tools){assert.equal(t.annotations.readOnlyHint,true);assert.equal(t.annotations.destructiveHint,false);assert.ok(t.outputSchema);assert.equal(t.inputSchema.properties.command,undefined);assert.equal(t.inputSchema.properties.path,undefined);}
  const resource=await client.readResource({uri:'ui://startup-jury/result-v1.html'});
  assert.equal(resource.contents[0].mimeType,'text/html;profile=mcp-app');
  assert.deepEqual(resource.contents[0]._meta.ui.csp.connectDomains,[]);
  assert.ok(resource.contents[0].text.includes('STARTUP JURY'));
  const invalid=await client.callTool({name:'get_evaluation',arguments:{evaluation_id:'../../config.toml'}});assert.equal(invalid.isError,true);
  const absent=await client.callTool({name:'get_evaluation',arguments:{evaluation_id:'00000000000000000000000000000000'}});assert.equal(absent.isError,true);assert.ok(absent.content[0].text.includes('not found'));
  const health=await client.callTool({name:'health_check',arguments:{}});assert.equal(health.isError,true);assert.equal(health.structuredContent.status,'BLOCKED');assert.match(health.structuredContent.runtime_validation,/NOT_RUN/);
  // A terminal engine failure must remain a tool error, not a successful verdict.
  const failedId='11111111111111111111111111111111';
  const failedFolder=testHome+'/jury-marketplace/startup-jury/jobs/'+failedId;
  fs.mkdirSync(failedFolder,{recursive:true,mode:0o700});
  fs.writeFileSync(failedFolder+'/state.json',JSON.stringify({evaluation_id:failedId,status:'FAILED',surface:'COMPUTER-ONLY',synthetic:true,started_at:0,completed_roles:[],started_roles:[],error:'Engine fixture failed'}));
  const failed=await client.callTool({name:'get_evaluation',arguments:{evaluation_id:failedId}});assert.equal(failed.isError,true);assert.match(failed.content[0].text,/NOT ISSUED/);
 }finally{await client.close();}
});
test('private adapter rejects command injection fields before creating any job',()=>{
 const r=spawnSync('python3',[root+'scripts/jobs.py','start'],{input:JSON.stringify({request:'synthetic',request_id:'security-check',command:'touch unsafe'}),encoding:'utf8'});
 assert.notEqual(r.status,0);assert.equal(JSON.parse(r.stdout).error,'Unknown input fields');
});
test('same request id retrieves existing terminal result and rejects changed input',()=>{
 // Populate only a test-owned completed job; this test cannot launch the Jury.
 const isolated=fs.mkdtempSync(os.tmpdir()+'/startup-jury-adapter-test-');
 const script=`import sys,json,hashlib,uuid\nfrom pathlib import Path\nsys.path.insert(0,${JSON.stringify(root+'scripts')})\nfrom jobs import ROOT,write,start,initialize\ninitialize()\njid=uuid.uuid4().hex;p=ROOT/jid;p.mkdir(mode=0o700)\nkey='adapter-test-'+jid\na={'request':'fixture','request_id':key,'synthetic_test':True}\nreg=ROOT/'registry.json';old=json.loads(reg.read_text()) if reg.exists() else {}\ntry:\n write(p/'state.json',{'evaluation_id':jid,'status':'FAILED','error':'test-owned fixture'})\n current=dict(old);current[hashlib.sha256(key.encode()).hexdigest()]={'id':jid,'digest':hashlib.sha256(json.dumps(['fixture',True]).encode()).hexdigest()};write(reg,current)\n assert start(a)['evaluation_id']==jid\n try:start({**a,'request':'changed'})\n except ValueError:pass\n else:raise AssertionError('changed input accepted')\nfinally:\n write(reg,old)\n (p/'state.json').unlink();p.rmdir()\nprint('passed')`;
 const r=spawnSync('python3',['-c',script],{encoding:'utf8',env:{...process.env,TMPDIR:isolated,CODEX_HOME:isolated}});fs.rmSync(isolated,{recursive:true});assert.equal(r.status,0,r.stderr);
});
