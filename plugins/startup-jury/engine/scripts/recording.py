"""Preserve native child reports without giving Stage 1 access to peer output."""
import hashlib
import json
from pathlib import Path
import re

STAGE_ONE = ['startup_customer_demand','startup_market_timing','startup_landscape',
             'startup_distribution','startup_economics','startup_product_execution',
             'startup_advocate','startup_skeptic']
LATER = ['startup_verifier','startup_cross_examiner','startup_judge']
FIRST_HEADINGS = ['BOTTOM LINE','STRONGEST EVIDENCE',
                  'STRONGEST ARGUMENT AGAINST MY OWN CONCLUSION',
                  'DECISION-CRITICAL HYPOTHESES','RISKS','RESULT','CONFIDENCE']

class Recorder:
    def __init__(self, directory, seed=None):
        self.directory=Path(directory)
        self.directory.mkdir()
        self.agents={}
        self.current={}
        self.reports={}
        self.states={}
        self.packet=None
        self.events=[]
        self.attempted=set()
        self.sealed=False
        if seed:
            for role in STAGE_ONE:
                self.reports[role]=(Path(seed)/'reports'/f'{role}.md').read_text()
            self.sealed=True
            self.publish()

    def publish(self):
        folder=self.directory/'reports'
        folder.mkdir(exist_ok=True)
        entries=[]
        for role,report in self.reports.items():
            target=folder/f'{role}.md'
            if target.exists() and target.read_text()!=report:
                raise RuntimeError('Attempt to change a sealed report: '+role)
            if not target.exists():
                target.write_text(report)
                target.chmod(0o400)
            entries.append({'role':role,'path':str(target),
                            'sha256':hashlib.sha256(report.encode()).hexdigest()})
        manifest={'reports':entries,'missing_stage_one':[r for r in STAGE_ONE if r not in self.reports],
                  'execution_states':{aid:{'role':self.agents.get(aid),'status':state} for aid,state in self.states.items()},
                  'packet':self.packet,
                  'state_note':'The current reader may still be pending/running. Judge completeness from required predecessor roles, not from the current role state.'}
        target=self.directory/'manifest.json'
        temporary=self.directory/'manifest.pending'
        temporary.write_text(json.dumps(manifest,indent=2))
        temporary.replace(target)

    def accept(self,event):
        self.events.append(event)
        item=event.get('item',{})
        if item.get('type')!='collab_tool_call':
            return
        prompt=item.get('prompt') or ''
        if item.get('tool')=='spawn_agent':
            match=re.search(r'^ROLE_NAME:\s*(startup_\w+)\s*$',prompt,re.M)
            if not match or match.group(1) not in STAGE_ONE+LATER:
                raise RuntimeError('Native spawn is missing its exact ROLE_NAME routing label')
            role=match.group(1)
            self.attempted.add(role)
            if role in STAGE_ONE:
                if self.sealed:
                    raise RuntimeError('Stage 1 cannot restart after its records are sealed for later stages')
                packet=re.search(r'BEGIN FROZEN STARTUP PACKET\n(.*?)\nEND FROZEN STARTUP PACKET',prompt,re.S)
                if not packet:
                    raise RuntimeError('Stage 1 spawn did not contain the complete delimited frozen packet')
                body=packet.group(1)
                if self.packet is None:
                    self.packet=body
                elif body!=self.packet:
                    raise RuntimeError('Stage 1 packets differ; independent evaluation is invalid')
                if any(r in self.reports for r in LATER):
                    raise RuntimeError('Stage 1 cannot restart after later-stage reports exist')
            else:
                unattempted=[r for r in STAGE_ONE if r not in self.attempted and r not in self.reports]
                if unattempted:
                    raise RuntimeError('Stage 1 roles were never attempted: '+', '.join(unattempted))
                pending=[aid for aid,state in self.states.items() if state not in ['completed','errored','failed','shutdown','invalid']]
                if pending:
                    raise RuntimeError('Later stage started before earlier children finished')
                if str(self.directory) not in prompt:
                    raise RuntimeError('Later stage did not receive the complete report directory')
                predecessor={'startup_cross_examiner':'startup_verifier','startup_judge':'startup_cross_examiner'}.get(role)
                if predecessor and predecessor not in self.attempted and predecessor not in self.reports:
                    raise RuntimeError('Required prior stage was never attempted: '+predecessor)
                # Preserve all captured originals before a downstream child reads them.
                self.sealed=True
                self.publish()
                if role=='startup_cross_examiner' and 'startup_verifier' not in self.reports and 'verification' not in prompt.lower():
                    raise RuntimeError('Cross-examiner lacks verifier output or an explicit verification limitation')
                if role=='startup_judge' and 'startup_cross_examiner' not in self.reports and 'cross-examination' not in prompt.lower():
                    raise RuntimeError('Judge lacks cross-examiner output or an explicit cross-examination limitation')
            if event['type']=='item.completed':
                for aid in item.get('receiver_thread_ids',[]):
                    if role in STAGE_ONE and aid not in self.agents:
                        # A fresh retry replaces an earlier incomplete candidate before sealing.
                        self.reports.pop(role,None)
                    self.agents[aid]=role
                    self.current[role]=aid
                    self.states[aid]='pending_init'
        for aid,state in item.get('agents_states',{}).items():
            self.states[aid]=state.get('status','unknown')
            if state.get('status')=='completed' and state.get('message'):
                role=self.agents.get(aid)
                if not role:
                    raise RuntimeError('Completed child has no native spawn routing record')
                if self.current.get(role)!=aid:
                    continue
                message=state['message']
                if role in STAGE_ONE and any(not re.search(r'^#{1,3}\s+'+re.escape(heading)+r'\s*$',message,re.M) for heading in FIRST_HEADINGS):
                    self.states[aid]='invalid'
                    continue
                if role in self.reports and self.reports[role]!=message:
                    raise RuntimeError('Completed report unexpectedly changed: '+role)
                self.reports[role]=message
        # Seal only at the Stage 2 boundary so an independent retry cannot see peers.
        if self.sealed:
            self.publish()
