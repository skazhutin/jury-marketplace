#!/usr/bin/env python3
"""Start only the bundled Project Jury MCP server; no downloads or shell."""
import os
from pathlib import Path
import sys

if sys.version_info < (3, 11):
    raise SystemExit("Jury plugins require Python 3.11 or newer on PATH.")
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'engine' / 'scripts'))
from native_runtime import resolve_node
try:
    node, version = resolve_node()
except RuntimeError as error:
    raise SystemExit(str(error))
allowed = {'PATH', 'HOME', 'USER', 'LOGNAME', 'TMPDIR', 'LANG', 'LC_ALL', 'CODEX_HOME', 'SSL_CERT_FILE', 'SSL_CERT_DIR', 'JURY_CODEX_BINARY'}
env = {k: v for k, v in os.environ.items() if k in allowed}
env['PROJECT_JURY_PYTHON'] = sys.executable
os.execve(node, [node, str(root / 'server/bundle.mjs')], env)
