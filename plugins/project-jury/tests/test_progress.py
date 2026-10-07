"""Operational events cannot disclose prompts, reports or private reasoning."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'engine/scripts'))
from runtime_progress import RunProgress


class ProgressTests(unittest.TestCase):
    def test_metadata_only_and_completed_context_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'progress.json'
            progress = RunProgress(path)
            item = {'id':'tool-1','type':'collab_tool_call','tool':'spawn_agent',
                    'prompt':'PRIVATE_PACKET','agents_states':{
                        'native-child':{'status':'completed','message':'INTENTIONAL_PRIVATE_REPORT'}}}
            progress.update({'type':'item.started','item':item})
            progress.update({'type':'item.completed','item':item})
            progress.update({'type':'item.completed','item':{'id':'reasoning-1','type':'reasoning','text':'PRIVATE_REASONING'}})
            value = json.loads(path.read_text())
            self.assertEqual(value['collaboration_counts'], {'spawn_agent':1})
            self.assertEqual(value['agent_counts'], {'completed':1})
            self.assertEqual(value['event_count'], 3)
            for secret in ['PRIVATE_PACKET','INTENTIONAL_PRIVATE_REPORT','PRIVATE_REASONING','native-child']:
                self.assertNotIn(secret, path.read_text())

    def test_running_context_transitions_without_double_count(self):
        with tempfile.TemporaryDirectory() as directory:
            progress = RunProgress(Path(directory)/'progress.json')
            for status in ['running','completed']:
                progress.update({'type':'item.completed','item':{'id':'wait-'+status,
                    'type':'collab_tool_call','tool':'wait','agents_states':{'child':{'status':status}}}})
            self.assertEqual(progress.value['agent_counts'], {'completed':1})


if __name__ == '__main__': unittest.main()
