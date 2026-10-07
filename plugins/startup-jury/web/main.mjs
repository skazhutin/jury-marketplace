import {App} from '@modelcontextprotocol/ext-apps';
import {render} from './view.mjs';
const root=document.getElementById('jury');let current=null;let meta={};let timer;let connected=false;
const app=new App({name:'Startup Jury',version:__JURY_VERSION__},{});
function update(result){
  if(result.isError){clearTimeout(timer);current={status:'FAILED',synthetic:result.structuredContent?.synthetic??current?.synthetic??false,error:result.content?.filter(x=>x.type==='text').map(x=>x.text).join('\n')||'The evaluation could not be retrieved.'};render(root,current);return;}
  if(!result.structuredContent)return;
  current=result.structuredContent;meta=result._meta?.startupJuryDetails||{};render(root,current,meta);
  clearTimeout(timer);
  if(current.status==='RUNNING'&&connected)timer=setTimeout(refresh,30000);
}
async function refresh(){
  try{update(await app.callServerTool({name:'show_evaluation',arguments:{evaluation_id:current.evaluation_id}}));}
  catch{document.getElementById('bridge-status').textContent='Automatic refresh is unavailable. Ask Startup Jury to retrieve this evaluation again.';}
}
app.ontoolresult=update;
app.onhostcontextchanged=ctx=>{if(ctx.theme)document.documentElement.dataset.theme=ctx.theme;};
render(root,null);
if(window.openai?.toolOutput)update({structuredContent:window.openai.toolOutput,_meta:window.openai.toolResponseMetadata});
window.addEventListener('openai:set_globals',event=>{if(event.detail?.globals?.toolOutput)update({structuredContent:event.detail.globals.toolOutput,_meta:event.detail.globals.toolResponseMetadata});});
app.connect().then(()=>{connected=true;const ctx=app.getHostContext();if(ctx?.theme)document.documentElement.dataset.theme=ctx.theme;if(current?.status==='RUNNING')timer=setTimeout(refresh,30000);}).catch(()=>{document.getElementById('bridge-status').textContent='Interactive host connection unavailable. The same Jury report remains available as text.';});
