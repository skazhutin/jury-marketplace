export function render(container,state,details={}) {
  container.replaceChildren();
  const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const appendText=(parent,text,cls='prose')=>{if(text)parent.append(el('div',text,cls));};
  const disclosure=(title,text,open=false)=>{const d=el('details');d.open=open;d.append(el('summary',title));appendText(d,text);return d;};
  const mast=el('header');mast.append(el('div','STARTUP JURY','brand'));mast.append(el('span','Business decision','subtitle'));container.append(mast);
  if(!state){appendText(container,'Your Jury result will appear here after an evaluation.','empty');return;}
  if(state.synthetic)appendText(container,'SYNTHETIC TEST — fictional evidence only; no real startup evaluated.','synthetic');
  if(state.status==='RUNNING'){
    const section=el('section');section.setAttribute('aria-live','polite');section.append(el('h1','Analysis in progress'));
    appendText(section,`${state.completed_roles.length} of 11 reports captured. Your result will update here.`);
    const p=el('progress');p.max=11;p.value=state.completed_roles.length;p.setAttribute('aria-label','Reports captured');section.append(p);
    if(state.started_roles.length)appendText(section,'Started: '+state.started_roles.map(s=>s.replace('startup_','').replaceAll('_',' ')).join(', '),'muted');container.append(section);return;
  }
  if(state.status==='FAILED'){
    const failure=el('section');failure.append(el('h1','NOT ISSUED'));appendText(failure,'ANALYSIS STATUS: BLOCKED');appendText(failure,'CONFIDENCE: LOW');appendText(failure,'BUSINESS OUTCOME: TOO EARLY TO CLASSIFY');appendText(failure,state.error,'error');appendText(failure,'Restore the local engine or missing capability, then run the evaluation again.');container.append(failure);return;
  }
  const r=state.result;
  if(!r){appendText(container,'The result payload is missing. Retrieve this evaluation again.','error');return;}
  const s=r.sections||{};
  const verdict=el('section',undefined,'decision');verdict.dataset.verdict=r.verdict;
  const stats=el('dl',undefined,'status-row');for(const [k,v] of [['ANALYSIS STATUS',r.analysis_status],['CONFIDENCE',r.confidence]]){const pair=el('div');pair.append(el('dt',k),el('dd',v));stats.append(pair);}verdict.append(stats);
  verdict.append(el('div','VERDICT','label'),el('h1',r.verdict));verdict.append(el('div','BUSINESS OUTCOME','label'),el('p',r.business_outcome,'outcome'));
  appendText(verdict,s['DECISIVE REASON']);container.append(verdict);
  const stateHead={PURSUE:'Next milestone','VALIDATE FIRST':'Decisive experiments',REFRAME:'Required reframe',REJECT:'Decisive reason and rescue evidence','NOT ISSUED':'What blocks adjudication'}[r.verdict];
  const next=el('section',undefined,'next');next.append(el('h2',stateHead));
  if(r.verdict==='VALIDATE FIRST' && r.experiments?.length){
    r.experiments.forEach((experiment,i)=>{const x=el('article');x.append(el('h3',`Experiment ${i+1}`));
      for(const key of ['HYPOTHESIS','TEST','PASS','FAIL','INCONCLUSIVE','COST OF LEARNING','EXPECTED TIME / EFFORT TO EVIDENCE','CAPITAL / RESOURCE INTENSITY','IRREVERSIBILITY','CHEAPEST CREDIBLE TEST','WHAT PASS WOULD NOT PROVE'])if(experiment.fields[key]){x.append(el('h4',key));appendText(x,experiment.fields[key]);}
      x.append(disclosure('Full experiment and measurement conditions',experiment.text));next.append(x);});
  }else if(r.verdict==='REFRAME' && /^#{2,6} PRESERVE/m.test(s['NEXT DECISION']||'')){
    const raw=s['NEXT DECISION'];const parts=[...raw.matchAll(/^#{2,6} (PRESERVE|CHANGE|WHY)\s*$/gm)];
    for(let i=0;i<parts.length;i++){next.append(el('h4',parts[i][1]));appendText(next,raw.slice(parts[i].index+parts[i][0].length,parts[i+1]?.index??raw.length).trim());}
  }else appendText(next,s['NEXT DECISION']||s['ANALYSIS STATUS']||'Inspect the original Judge report for the next decision.');
  if(r.verdict==='REJECT')appendText(next,s['WHAT WOULD CHANGE THE VERDICT']);
  if(r.verdict==='NOT ISSUED')appendText(next,s['ANALYSIS STATUS']);
  container.append(next);
  const dimensions=el('section');dimensions.append(el('h2','Business dimensions'));
  for(const [title,key] of [['Customer / Demand','CUSTOMER / DEMAND REALITY'],['Market','MARKET REALITY'],['Competition','COMPETITIVE REALITY'],['Distribution','DISTRIBUTION REALITY'],['Economics','ECONOMIC REALITY'],['Product / Execution','PRODUCT / EXECUTION REALITY'],['Business System','BUSINESS SYSTEM CHECK'],['Evidence','EVIDENCE QUALITY'],['Standalone Business','STANDALONE BUSINESS TEST'],['Cost of Learning','COST OF LEARNING'],['Right to Win','RIGHT TO WIN'],['Expansion','EXPANSION LOGIC']]){
    let text=s[key];if(key==='RIGHT TO WIN'&&!text)text='UNKNOWN — do not infer.';if(!text)continue;
    const row=el('article',undefined,'dimension');row.append(el('h3',title));
    if(text.length<=420)appendText(row,text);else{appendText(row,text.slice(0,420).replace(/\s+\S*$/,'')+'…');row.append(disclosure('Read full conclusion',text));}dimensions.append(row);
  }container.append(dimensions);
  const evidence=el('section');evidence.append(el('h2','Inspect the record'));
  const registry=el('details');registry.append(el('summary','Decision-critical claim registry'));
  for(const claim of details.claims||[])appendText(registry,`${claim.id}\nReferenced in: ${claim.reports.join(', ')}`);
  registry.append(disclosure('Claim records and verification',details.reports?.find(x=>x.role==='startup_verifier')?.text||'No Verifier report available.'));
  evidence.append(registry);
  const sources=el('details');sources.append(el('summary','Sources / evidence'));
  for(const url of details.sources||[]){try{const parsed=new URL(url);if(!['https:','http:'].includes(parsed.protocol))continue;const a=el('a',url);a.href=parsed.href;a.target='_blank';a.rel='noopener noreferrer';sources.append(a);}catch{}}
  if(!details.sources?.length)appendText(sources,'No external source URLs recorded. User-reported and synthetic evidence remain labeled in the reports.');evidence.append(sources);
  evidence.append(disclosure('Material disagreements',s['AGENT DISAGREEMENTS']||'No material disagreements recorded.'));
  const originals=el('details');originals.append(el('summary','All eleven original reports'));
  for(const report of details.reports||[]){const d=disclosure(report.role.replace('startup_','').replaceAll('_',' '),report.text);appendText(d,`Report SHA-256: ${report.sha256 || 'Not reported.'}`,'hash');originals.append(d);}evidence.append(originals);
  evidence.append(disclosure('Judge report / text fallback',r.text_report));
  evidence.append(disclosure('Execution limitations',[s['ANALYSIS STATUS'],...(r.limitations||[])].filter(Boolean).join('\n\n')));
  evidence.append(disclosure('Runtime validation metadata',JSON.stringify(details.runtime||{},null,2)));
  container.append(evidence);appendText(container,'Confidence describes the assessment, not the probability of startup success.','footer');
}
