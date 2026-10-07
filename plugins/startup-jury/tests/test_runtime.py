"""Regressions for runtime selection and readiness failure reporting; no model calls."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine' / 'scripts'))
from native_runtime import REQUIRED_FLAGS, resolve_codex, resolve_node
sys.path.insert(0, str(ROOT / 'scripts'))
from doctor import health


def response(args, **kwargs):
    if args[-1] == '--version':
        return subprocess.CompletedProcess(args, 0, 'codex-cli fixture', '')
    if args[-1] == '--help':
        flags = '--json' if args[0] == '/old/codex' else ' '.join(REQUIRED_FLAGS)
        return subprocess.CompletedProcess(args, 0, flags, '')
    raise AssertionError(args)


class RuntimeTests(unittest.TestCase):
    @patch.dict(os.environ, {'JURY_CODEX_BINARY': '/chosen/codex'})
    @patch('native_runtime.subprocess.run', side_effect=response)
    def test_explicit_runtime_is_selected(self, run):
        self.assertEqual(resolve_codex()[0], str(Path('/chosen/codex').resolve()))
        self.assertEqual(run.call_count, 2)

    @patch.dict(os.environ, {'JURY_CODEX_BINARY': '/old/codex'})
    @patch('native_runtime.subprocess.run', side_effect=response)
    def test_unsupported_explicit_runtime_never_falls_back(self, run):
        with self.assertRaisesRegex(RuntimeError, 'lacks.*--ignore-user-config'):
            resolve_codex()
        self.assertEqual(run.call_count, 2)

    @patch.dict(os.environ, {}, clear=True)
    @patch('native_runtime.shutil.which', return_value='/old/codex')
    @patch('native_runtime.subprocess.run', side_effect=response)
    def test_old_path_runtime_can_fall_back_to_compatible_desktop(self, run, which):
        self.assertIn('/Applications/', resolve_codex()[0])

    @patch('native_runtime.shutil.which', return_value='/old/node')
    @patch('native_runtime.subprocess.run')
    def test_old_node_falls_back_to_supported_desktop_node(self, run, which):
        run.side_effect = [subprocess.CompletedProcess([], 0, 'v18.0.0', ''),
                           subprocess.CompletedProcess([], 0, 'v24.0.0', '')]
        self.assertEqual(resolve_node()[1], 'v24.0.0')

    @patch('doctor.resolve_codex', side_effect=RuntimeError('Missing runtime fixture'))
    def test_health_reports_blockage_without_starting_an_evaluation(self, resolve):
        result = health()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('NOT_RUN', result['runtime_validation'])
        self.assertTrue(any(c['detail'] == 'Missing runtime fixture' for c in result['checks']))

    @patch('doctor.resolve_codex', return_value=('/chosen/codex', 'codex-cli fixture'))
    @patch('doctor.resolve_node', return_value=('/chosen/node', 'v24.0.0'))
    @patch('doctor.subprocess.run')
    def test_login_failure_is_not_ready_and_credential_output_is_never_returned(self, run, node, resolve):
        run.return_value = subprocess.CompletedProcess([], 1, 'PRIVATE_TOKEN', 'PRIVATE_TOKEN')
        result = health()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertNotIn('PRIVATE_TOKEN', str(result))


if __name__ == '__main__':
    unittest.main()
