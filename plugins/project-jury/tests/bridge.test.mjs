import test from 'node:test';
import assert from 'node:assert/strict';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';

test('shipped Project Jury server exposes working health and instruction resources',async()=>{
  const root=fileURLToPath(new URL('../',import.meta.url));
  const home=mkdtempSync(join(tmpdir(),'project-jury-bridge-'));
  const client=new Client({name:'project-jury-contract',version:'1.0.0'});
  try {
    await client.connect(new StdioClientTransport({command:'python3',args:[root+'scripts/start_server.py'],cwd:root,stderr:'pipe',env:{...process.env,CODEX_HOME:home,JURY_CODEX_BINARY:'/missing-jury-test-runtime'}}));
    const {tools}=await client.listTools();
    assert.deepEqual(tools.map(t=>t.name).sort(),['get_result','health_check','submit_evaluation']);
    const health=await client.callTool({name:'health_check',arguments:{}});
    assert.equal(health.isError,true);assert.equal(health.structuredContent.status,'BLOCKED');
    assert.match(health.structuredContent.runtime_validation,/NOT_RUN/);
    const invalid=await client.callTool({name:'health_check',arguments:{path:'/private'}});
    assert.equal(invalid.isError,true);
    const resource=await client.readResource({uri:'jury://instructions/packet'});
    assert.equal(resource.contents[0].mimeType,'text/markdown');
    assert.match(resource.contents[0].text,/PROJECT TYPE/);
    const ui=await client.readResource({uri:'ui://project-jury/result-v1.html'});
    assert.equal(ui.contents[0].mimeType,'text/html;profile=mcp-app');
    assert.deepEqual(ui.contents[0]._meta.ui.csp.connectDomains,[]);
  } finally {
    await client.close();rmSync(home,{recursive:true,force:true});
  }
});
