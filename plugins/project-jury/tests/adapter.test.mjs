import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const temp=mkdtempSync(join(tmpdir(),'jury-adapter-test-'));
process.env.CODEX_HOME=temp;
const {validateSubmission,retrieve,submit,toolResult,sections,packetFields,jobsRoot,safeProgress}=await import('../server/adapter.mjs');
const id='d0b1d039-b0e9-4d22-92dd-ea878f795a5d';
const synthetic={request_id:id,mode:'synthetic_validation',packet:{},common_sources:[]};
test.after(()=>rmSync(temp,{recursive:true,force:true}));
test('rejects path traversal and arbitrary extra arguments',()=>{
 assert.throws(()=>retrieve('../../config.toml'),/UUID/);
 assert.throws(()=>validateSubmission({...synthetic,command:'id'}),/Unsupported/);
});
test('synthetic mode cannot silently discard a supplied real idea',()=>{
 assert.throws(()=>validateSubmission({...synthetic,packet:{idea:'real idea'}}),/no project content/);
});
test('normal evaluation requires every frozen packet field',()=>{
 assert.throws(()=>validateSubmission({request_id:id,mode:'evaluation',packet:{},common_sources:[]}),/complete frozen/);
 const packet=Object.fromEntries(packetFields.map(k=>[k,'User supplied text']));
 assert.deepEqual(validateSubmission({request_id:id,mode:'evaluation',packet,common_sources:[]}).packet,packet);
});
test('bounds content passed to existing engine',()=>assert.throws(()=>validateSubmission({...synthetic,packet:{large:'x'.repeat(160000)}}),/150 KB/));
test('idempotent submission retrieves existing job without re-running engine',()=>{
 mkdirSync(join(jobsRoot,id),{recursive:true});
 writeFileSync(join(jobsRoot,id,'request.json'),JSON.stringify(synthetic));
 writeFileSync(join(jobsRoot,id,'status.json'),JSON.stringify({job_id:id,job_status:'FINISHED',synthetic:true}));
 assert.equal(submit(synthetic).job_status,'FINISHED');
 assert.throws(()=>submit({...synthetic,mode:'evaluation',packet:Object.fromEntries(packetFields.map(k=>[k,'different']))}),/different frozen/);
});
test('unknown job cannot read arbitrary file',()=>assert.throws(()=>retrieve('deadbeef-dead-beef-dead-beefdeadbeef'),/not found/));
test('text fallback preserves verbatim Judge report; hidden trace fields excluded',()=>{
 const report='# ANALYSIS STATUS\nBLOCKED\n\n# VERDICT\nNOT ISSUED\n\n# CONFIDENCE\nLOW\n\n# DECISIVE REASON\nSynthetic test only.';
 const result=toolResult({job_id:id,job_status:'FINISHED',synthetic:true,hidden_reasoning:'NEVER_RETURN',result:{analysis_status:'BLOCKED',verdict:'NOT ISSUED',final_report:report,roles:[{role:'project_value',report:'Intentional role output'}],limitations:[],permission_evidence:'Intentional evidence'}});
 assert.equal(result.structuredContent.confidence,'LOW');
 assert.equal(result.content[0].text,'# PROJECT JURY\n\n'+report);
 assert.equal(result._meta.juryDetail.roles.length,1);
 assert.ok(!JSON.stringify(result).includes('NEVER_RETURN'));
});
test('heading compatibility handles enum suffix and subordinate headings',()=>{
 const p=sections('# CONFIDENCE (LOW)\nSynthetic.\n# DECISIVE REASON\nMain\n## Supporting detail\nPreserved');
 assert.match(p.CONFIDENCE,/^LOW/);assert.match(p['DECISIVE REASON'],/Supporting detail/);
 const r=toolResult({job_id:id,job_status:'FINISHED',result:{final_report:'# CONFIDENCE (LOW)\nSynthetic.',roles:[]}});
 assert.equal(r.structuredContent.confidence,'LOW');
 const labelled=toolResult({job_id:id,job_status:'FINISHED',result:{final_report:'# CONFIDENCE\nCONFIDENCE=LOW',roles:[]}});
 assert.equal(labelled.structuredContent.confidence,'LOW');
});
test('failure is an evaluation blockage, never a negative project verdict',()=>{
 const r=toolResult({job_id:id,job_status:'FAILED',error:'Runtime unavailable'});
 assert.equal(r.structuredContent.analysis_status,'BLOCKED');assert.equal(r.structuredContent.verdict,'NOT ISSUED');assert.equal(r.isError,true);
});
test('progress projection rejects runtime text and never implies a Jury verdict',()=>{
 const progress = {event_count:5,last_event_at:42,last_activity:'collab_tool_call',
   agent_counts:{completed:1,PRIVATE_REASONING:10},collaboration_counts:{spawn_agent:1},
   item_counts:{collab_tool_call:2},prompt:'PRIVATE_PACKET',report:'PRIVATE_REPORT'};
 const state=toolResult({job_id:id,job_status:'RUNNING',progress});
 assert.equal(state.structuredContent.analysis_status,'PENDING');
 assert.equal(state.structuredContent.verdict,'NOT ISSUED');
 assert.deepEqual(state.structuredContent.runtime.progress.agent_counts,{completed:1});
 assert.ok(!JSON.stringify(state).includes('PRIVATE'));
 assert.equal(safeProgress({event_count:-1,last_activity:'SECRET',item_counts:{web_search:NaN}}).last_activity,'starting');
});
