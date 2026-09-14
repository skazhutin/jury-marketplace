"""Regression checks for real handoff invariants and lossless presentation."""
import json
from pathlib import Path
import tempfile
import unittest
from recording import Recorder, STAGE_ONE, FIRST_HEADINGS
from result import build_result

def report(claim='INPUT:C001'):
    return '\n'.join('## '+h+'\n'+claim for h in FIRST_HEADINGS)

def spawn(role,aid,packet='frozen'):
    return {'type':'item.completed','item':{'type':'collab_tool_call','tool':'spawn_agent','prompt':f'ROLE_NAME: {role}\nBEGIN FROZEN STARTUP PACKET\n{packet}\nEND FROZEN STARTUP PACKET','receiver_thread_ids':[aid]}}

def completed(aid,text):return {'type':'item.completed','item':{'type':'collab_tool_call','tool':'wait','agents_states':{aid:{'status':'completed','message':text}}}}

class RecorderTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.r=Recorder(Path(self.temp.name)/'records')
    def tearDown(self):self.temp.cleanup()
    def test_independence_and_exact_handoff(self):
        for i,role in enumerate(STAGE_ONE):
            self.r.accept(spawn(role,str(i)));self.r.accept(completed(str(i),report()))
        self.assertFalse((self.r.directory/'reports').exists())
        event=spawn('startup_verifier','v');event['item']['prompt']+='\nRECORDS_DIR: '+str(self.r.directory)
        self.r.accept(event)
        for role in STAGE_ONE:self.assertEqual((self.r.directory/'reports'/f'{role}.md').read_text(),report())
        self.assertEqual(len(self.r.agents),9)
    def test_packet_mismatch_fails(self):
        self.r.accept(spawn(STAGE_ONE[0],'a'))
        with self.assertRaises(RuntimeError):self.r.accept(spawn(STAGE_ONE[1],'b','changed'))
    def test_retry_cannot_see_peers_or_be_overwritten_by_old_attempt(self):
        self.r.accept(spawn(STAGE_ONE[0],'old'));self.r.accept(completed('old',report()))
        self.r.accept(spawn(STAGE_ONE[0],'new'));self.r.accept(completed('old',report()))
        self.assertNotIn(STAGE_ONE[0],self.r.reports)
        self.assertFalse((self.r.directory/'reports').exists())
        self.r.accept(completed('new',report('INPUT:C002')))
        self.assertIn('INPUT:C002',self.r.reports[STAGE_ONE[0]])
    def test_incomplete_stage_cannot_start_verifier(self):
        self.r.accept(spawn(STAGE_ONE[0],'a'))
        e=spawn('startup_verifier','v');e['item']['prompt']+=str(self.r.directory)
        with self.assertRaises(RuntimeError):self.r.accept(e)
    def test_public_projection_is_lossless_and_not_a_new_judgment(self):
        text='# ANALYSIS STATUS\nLIMITED\n# VERDICT\nVALIDATE FIRST\n# CONFIDENCE\nLOW\n# BUSINESS OUTCOME\nTOO EARLY TO CLASSIFY\n# NEXT DECISION\n### HYPOTHESIS\nINPUT:C001\n### TEST\nA test\n### PASS\nA pass\n### FAIL\nA fail\n### INCONCLUSIVE\nNo discrimination\n### COST OF LEARNING\nCHEAP TO TEST\n### WHAT PASS WOULD NOT PROVE\nThe entire business'
        self.r.reports['startup_judge']=text
        result=build_result(self.r,{'write_denied':True})
        self.assertEqual(result['text_report'],text)
        self.assertEqual(result['verdict'],'VALIDATE FIRST')
        self.assertEqual(result['experiments'][0]['fields']['COST OF LEARNING'],'CHEAP TO TEST')
        self.assertEqual(result['reports'][0]['text'],text)
        self.assertEqual(result['claims'][0]['id'],'INPUT:C001')
        self.r.reports['startup_judge']=text.replace('VALIDATE FIRST','99% success')
        result=build_result(self.r,{})
        self.assertEqual(result['verdict'],'NOT ISSUED');self.assertEqual(result['analysis_status'],'BLOCKED')
        self.assertTrue(result['limitations'])

if __name__=='__main__':unittest.main()
