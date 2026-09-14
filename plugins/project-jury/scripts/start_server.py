#!/usr/bin/env python3
"""Start only the bundled Project Jury MCP server; no downloads or shell."""
import os
from pathlib import Path
import shutil
import sys

if sys.version_info < (3, 11):
    raise SystemExit("Jury plugins require Python 3.11 or newer on PATH.")
root = Path(__file__).resolve().parents[1]
bundled = Path('/Applications/ChatGPT.app/Contents/Resources/cua_node/bin/node')
node = str(bundled) if bundled.is_file() else shutil.which('node')
if not node:
    raise SystemExit('Project Jury requires Node.js 20+ on this computer.')
allowed = {'PATH', 'HOME', 'USER', 'LOGNAME', 'TMPDIR', 'LANG', 'LC_ALL', 'CODEX_HOME', 'SSL_CERT_FILE', 'SSL_CERT_DIR'}
env = {k: v for k, v in os.environ.items() if k in allowed}
env['PROJECT_JURY_PYTHON'] = sys.executable
os.execve(node, [node, str(root / 'server/bundle.mjs')], env)
