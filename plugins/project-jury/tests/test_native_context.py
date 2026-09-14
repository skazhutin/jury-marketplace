"""No model calls: exercise the production native-context and acceptance gates."""
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import tomllib
import unittest

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
sys.path.insert(0, str(ENGINE / 'scripts'))
from native_runtime import prepare_agents, reference_receipts, validate_agents
from run_jury import ROLES, STAGE_ONE, validate_result, section_value


def completion():
    report = '\n\n'.join('# '+heading+'\n'+
                         ('UNCERTAIN' if heading=='RESULT' else 'LOW' if heading=='CONFIDENCE'
                          else 'Synthetic contract fixture; no project evaluated.')
                         for heading in STAGE_ONE)
    report += '\n\nJURY_REFERENCE_RECEIPTS: ' + json.dumps(reference_receipts(ENGINE, ROLES[0]))
    roles = [{'role':name, 'native_agent_id':'', 'status':'not_started', 'attempts':0,
              'input_hash':'', 'received_reports':[], 'sibling_report_visible_before_submission':False,
              'report':'', 'failure':''} for name in ROLES]
    roles[0].update(native_agent_id='synthetic-context',status='complete',attempts=1,input_hash='fixture',report=report)
    return {'analysis_status':'BLOCKED','verdict':'NOT ISSUED','final_report':'Synthetic acceptance test only.',
            'roles':roles,'stage_sequence':[], 'limitations':['Not a Jury evaluation.'],
            'canary_attempted':True,'canary_denied':True,'permission_evidence':'Synthetic validator input only.',
            'web_probe_succeeded':False}


class NativeContextTests(unittest.TestCase):
    def test_complete_receipts_are_accepted(self):
        validate_result(completion(), 'fixture', False)

    def test_enum_punctuation_preserves_exact_value_boundary(self):
        for body in ["LOW", "LOW: explanation", "LOW, because synthetic", "LOW. Explanation"]:
            self.assertEqual(section_value("# CONFIDENCE\n"+body, "CONFIDENCE"), "LOW")
        for body in ["LOWISH", "LOW/HIGH", "NOT LOW"]:
            self.assertNotEqual(section_value("# CONFIDENCE\n"+body, "CONFIDENCE"), "LOW")

    def test_missing_receipt_rejects_completed_role(self):
        result = completion()
        receipt = reference_receipts(ENGINE, ROLES[0])
        receipt.pop(next(iter(receipt)))
        result['roles'][0]['report'] = re.sub(r'JURY_REFERENCE_RECEIPTS: .*',
                                           'JURY_REFERENCE_RECEIPTS: '+json.dumps(receipt),
                                           result['roles'][0]['report'])
        with self.assertRaisesRegex(ValueError, 'Incomplete or stale mandatory'):
            validate_result(result, 'fixture', False)

    def test_absent_and_forged_receipts_reject(self):
        for receipt in ['', 'JURY_REFERENCE_RECEIPTS: {}']:
            result = completion()
            result['roles'][0]['report'] = re.sub(r'JURY_REFERENCE_RECEIPTS: .*', receipt, result['roles'][0]['report'])
            with self.assertRaises(ValueError): validate_result(result, 'fixture', False)

    def test_all_native_roles_include_original_mandatory_context(self):
        with tempfile.TemporaryDirectory() as workspace:
            prepare_agents(workspace, ENGINE, ENGINE/'native_agents', ROLES)
            validate_agents(workspace, ENGINE, ROLES)
            for role in ROLES:
                file = Path(workspace)/'.codex/agents'/(role+'.toml')
                data = tomllib.loads(file.read_text())
                self.assertEqual(data['name'], role)
                for name in reference_receipts(ENGINE, role):
                    self.assertIn((ENGINE/name).read_text(), data['developer_instructions'])

    def test_removed_native_reference_fails_before_invocation(self):
        with tempfile.TemporaryDirectory() as workspace:
            prepare_agents(workspace, ENGINE, ENGINE/'native_agents', ROLES)
            file = Path(workspace)/'.codex/agents'/(ROLES[0]+'.toml')
            data = tomllib.loads(file.read_text())
            data['developer_instructions'] = data['developer_instructions'].split('BEGIN MANDATORY REFERENCE')[0]
            file.chmod(0o600)
            file.write_text('name = '+json.dumps(ROLES[0])+'\ndeveloper_instructions = '+json.dumps(data['developer_instructions']))
            with self.assertRaisesRegex(ValueError, 'Mandatory native context is incomplete'):
                validate_agents(workspace, ENGINE, ROLES)

    def test_missing_reference_file_fails_before_invocation(self):
        with tempfile.TemporaryDirectory() as empty, tempfile.TemporaryDirectory() as workspace:
            with self.assertRaises(FileNotFoundError):
                prepare_agents(workspace, empty, ENGINE/'native_agents', ROLES)


if __name__ == '__main__': unittest.main()
