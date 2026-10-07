#!/usr/bin/env python3
"""Model-free readiness checks. Never read credentials or launch an evaluation."""
import json
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine' / 'scripts'))
from native_runtime import resolve_codex, resolve_node


def health():
    package = json.loads((ROOT / 'package.json').read_text())
    checks = []

    def add(name, ok, detail):
        checks.append({'name': name, 'status': 'PASS' if ok else 'BLOCKED', 'detail': detail})

    add('python', sys.version_info >= (3, 11), 'Python ' + sys.version.split()[0])
    try:
        node, version = resolve_node()
        add('node', True, 'Node ' + version)
    except RuntimeError:
        add('node', False, 'Node.js 20+ is required')
    add('bundle', (ROOT / 'server' / 'bundle.mjs').is_file(), 'Bundled MCP server')
    try:
        profile = tomllib.loads((ROOT / 'engine' / 'runtime.toml').read_text())
        agents = [tomllib.loads(p.read_text()) for p in sorted((ROOT / 'engine' / 'native_agents').glob('*.toml'))]
        expected = 8 if package['name'] == 'project-jury' else 11
        safe = profile.get('sandbox_mode') == 'read-only' and profile.get('approval_policy') == 'never'
        safe = safe and profile.get('features', {}).get('multi_agent') is True
        safe = safe and all(profile.get('features', {}).get(k) is False for k in ['apps', 'plugins', 'hooks', 'image_generation'])
        safe = safe and len(agents) == expected and len({a.get('name') for a in agents}) == expected
        safe = safe and all(a.get('sandbox_mode') == 'read-only' and a.get('approval_policy') == 'never' for a in agents)
        add('native_roles', safe, f'{len(agents)}/{expected} roles; read-only / never required')
        models = sorted({profile['model'], *(a['model'] for a in agents)})
        add('configured_models', True, ', '.join(models) + '; remote access is checked when evaluating')
    except (OSError, ValueError, KeyError):
        add('native_roles', False, 'Bundled runtime or role configuration is invalid')
    try:
        binary, version = resolve_codex()
        add('codex', True, version + '; required isolation options supported')
        login = subprocess.run([binary, 'login', 'status'], capture_output=True, text=True, timeout=5)
        add('login', login.returncode == 0, 'Signed in to Codex' if login.returncode == 0 else 'Run codex login')
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        add('codex', False, str(error) if isinstance(error, RuntimeError) else 'Codex readiness check failed')
    return {'plugin': package['name'], 'version': package['version'],
            'status': 'READY' if all(c['status'] == 'PASS' for c in checks) else 'BLOCKED',
            'runtime_validation': 'NOT_RUN: no model request or evaluation is made by this check',
            'checks': checks}


if __name__ == '__main__':
    result = health()
    print(json.dumps(result))
    sys.exit(0 if result['status'] == 'READY' else 1)
