"""Presentation-only projection of intentionally produced Jury reports."""
import hashlib
import re
from recording import STAGE_ONE, LATER

STATUSES=['COMPLETE','LIMITED','BLOCKED']
VERDICTS=['PURSUE','VALIDATE FIRST','REFRAME','REJECT','NOT ISSUED']
OUTCOMES=['POTENTIAL VENTURE-SCALE COMPANY','POTENTIALLY STRONG BOOTSTRAPPED / NICHE BUSINESS','POSSIBLE SMALL BUSINESS','USEFUL PRODUCT, WEAK BUSINESS','NO CONVINCING BUSINESS MODEL','TOO EARLY TO CLASSIFY']

def sections(text, level=1):
    matches=list(re.finditer(r'^'+('#'*level)+r' (.+?)\s*$',text,re.M))
    return {m.group(1).strip().upper():text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)].strip() for i,m in enumerate(matches)}

def enum_value(body, allowed):
    first=next((s.strip(' `*\t\r') for s in body.splitlines() if s.strip()),'')
    for value in allowed:
        if first==value or re.match(re.escape(value)+r'(?:\s*[—–:.;(]|\s+-\s)',first):return value
    raise ValueError('Missing or invalid final status field')

def build_result(recorder, permissions, synthetic=False):
    original=recorder.reports.get('startup_judge','')
    parts=sections(original)
    limitations=[]
    try:
        status=enum_value(parts.get('ANALYSIS STATUS',''),STATUSES)
        verdict=enum_value(parts.get('VERDICT',''),VERDICTS)
        confidence=enum_value(parts.get('CONFIDENCE',''),['LOW','MEDIUM','HIGH'])
        outcome=enum_value(parts.get('BUSINESS OUTCOME',''),OUTCOMES)
        if (status=='BLOCKED') != (verdict=='NOT ISSUED'):raise ValueError('Inconsistent status and verdict')
    except ValueError:
        # Never infer a verdict from prose or silently repair an invalid Judge result.
        status,verdict,confidence,outcome='BLOCKED','NOT ISSUED','LOW','TOO EARLY TO CLASSIFY'
        limitations.append('The Judge report lacks valid machine-readable final status fields. Inspect the original report; adjudication was not translated into a verdict.')
    reports=[{'role':role,'agent_id':recorder.current.get(role),'text':recorder.reports[role],
              'sha256':hashlib.sha256(recorder.reports[role].encode()).hexdigest()}
             for role in STAGE_ONE+LATER if role in recorder.reports]
    ids=sorted(set(re.findall(r'\b(?:INPUT|startup_\w+):C\d+\b','\n'.join(r['text'] for r in reports))))
    claims=[{'id':cid,'reports':[r['role'] for r in reports if cid in r['text']]} for cid in ids]
    sources=sorted(set(re.findall(r'https?://[^\s<>\[\]"\)]+','\n'.join(r['text'] for r in reports))))
    experiments=[]
    fields=['HYPOTHESIS','WHY IT MATTERS','TEST','EVIDENCE TO COLLECT','PASS','FAIL','INCONCLUSIVE','THRESHOLD RATIONALE','MEASUREMENT CONDITIONS / CONFOUNDERS','WHAT PASS WOULD NOT PROVE','CONSEQUENCE','COST OF LEARNING','EXPECTED TIME / EFFORT TO EVIDENCE','CAPITAL / RESOURCE INTENSITY','IRREVERSIBILITY','CHEAPEST CREDIBLE TEST']
    next_decision=parts.get('NEXT DECISION','')
    starts=list(re.finditer(r'^#{2,6}\s+HYPOTHESIS\s*$',next_decision,re.M))
    for i,m in enumerate(starts):
        raw=next_decision[m.start():starts[i+1].start() if i+1<len(starts) else len(next_decision)].strip()
        heads=list(re.finditer(r'^#{2,6}\s+('+'|'.join(re.escape(x) for x in sorted(fields,key=len,reverse=True))+r')\s*$',raw,re.M))
        experiments.append({'fields':{h.group(1):raw[h.end():heads[j+1].start() if j+1<len(heads) else len(raw)].strip() for j,h in enumerate(heads)},'text':raw})
    missing=[r for r in STAGE_ONE+LATER if r not in recorder.reports]
    if missing:limitations.append('Missing reports: '+', '.join(missing))
    audit=[]
    for e in recorder.events:
        it=e.get('item',{})
        if it.get('type')=='collab_tool_call' and e.get('type')=='item.completed':
            audit.append({'tool':it.get('tool'),'receivers':it.get('receiver_thread_ids',[]),
                          'states':{aid:s.get('status') for aid,s in it.get('agents_states',{}).items()}})
    return {'schema_version':1,'synthetic':synthetic,'analysis_status':status,'verdict':verdict,
            'confidence':confidence,'business_outcome':outcome,'sections':parts,'experiments':experiments,
            'text_report':original,'reports':reports,'claims':claims,'sources':sources,
            'limitations':limitations,'runtime':{'engine':'existing-startup-jury','roles':dict(recorder.agents),
                'packet':recorder.packet,'packet_sha256':hashlib.sha256((recorder.packet or '').encode()).hexdigest(),
                'permissions':permissions,'handoff_recorder':'validated','missing_roles':missing,'lifecycle':audit}}
