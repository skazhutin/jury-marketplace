#!/usr/bin/env python3
"""Validate distributable metadata, bundled roles and isolation without model calls."""
import json
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = {'project-jury': 8, 'startup-jury': 11}


def validate():
    catalog = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
    assert {p['name'] for p in catalog['plugins']} == set(PLUGINS), 'Marketplace entries differ'
    versions = []
    for name, count in PLUGINS.items():
        root = ROOT / 'plugins' / name
        package = json.loads((root / 'package.json').read_text())
        versions.append(package['version'])
        assert re.fullmatch(r'\d+\.\d+\.\d+', package['version']), 'Use a release version'
        for filename in ['plugin.json', '.codex-plugin/plugin.json']:
            manifest = json.loads((root / filename).read_text())
            assert (manifest['name'], manifest['version']) == (name, package['version']), filename
        lock = json.loads((root / 'package-lock.json').read_text())
        assert lock['version'] == lock['packages']['']['version'] == package['version'], 'Lockfile version differs'
        assert lock['packages']['']['dependencies'] == package['dependencies'], 'Lockfile dependencies differ'
        mcp = json.loads((root / '.mcp.json').read_text())
        assert len(mcp['mcpServers']) == 1
        command = next(iter(mcp['mcpServers'].values()))
        assert command['command'] == 'python3' and command['args'] == ['./scripts/start_server.py']
        assert (root / 'scripts/start_server.py').is_file() and (root / 'scripts/doctor.py').is_file()
        assert (root / 'server/bundle.mjs').stat().st_size > 1000, 'Missing bundled server'
        assert (root / ('ui/result.html' if name == 'project-jury' else 'web/result.html')).is_file()
        profile = tomllib.loads((root / 'engine/runtime.toml').read_text())
        assert profile['sandbox_mode'] == 'read-only' and profile['approval_policy'] == 'never'
        assert profile['features']['multi_agent'] is True
        for feature in ['apps', 'plugins', 'hooks', 'image_generation']:
            assert profile['features'][feature] is False, feature
        roles = sorted((root / 'engine/native_agents').glob('*.toml'))
        assert len(roles) == count, 'Wrong role count'
        for file in roles:
            role = tomllib.loads(file.read_text())
            assert role['name'] == file.stem
            assert role['sandbox_mode'] == 'read-only' and role['approval_policy'] == 'never'
            assert role['features']['multi_agent'] is False, 'Specialists must not delegate'
            assert role['model'] and role['developer_instructions']
        entry = next(p for p in catalog['plugins'] if p['name'] == name)
        assert entry['source'] == {'source': 'local', 'path': './plugins/' + name}
        assert entry['policy']['installation'] == 'AVAILABLE'
    assert len(set(versions)) == 1, 'Coordinated release versions differ'
    # Each package is self-contained; keep the shared portable bootstrap identical.
    for file in ['engine/scripts/native_runtime.py', 'scripts/doctor.py']:
        assert (ROOT / 'plugins/project-jury' / file).read_bytes() == (ROOT / 'plugins/startup-jury' / file).read_bytes(), file
    print(f"Validated both Jury {versions[0]} packages and all 19 read-only native roles.")


if __name__ == '__main__':
    validate()
