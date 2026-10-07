#!/usr/bin/env python3
"""Regenerate production dependency notices from the installed, locked packages."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def update():
    for name in ['project-jury', 'startup-jury']:
        root = ROOT / 'plugins' / name
        lock = json.loads((root / 'package-lock.json').read_text())
        notices = ['# Bundled dependency notices\n']
        for location, package in sorted(lock['packages'].items()):
            if not location.startswith('node_modules/') or package.get('dev'):
                continue
            folder = root / location
            metadata = json.loads((folder / 'package.json').read_text())
            files = sorted(p for p in folder.iterdir() if p.is_file() and
                           p.name.upper().startswith(('LICENSE', 'LICENCE', 'COPYING')))
            if not files:
                raise ValueError('Missing dependency license: ' + location)
            notices.append(f"## {metadata['name']} {metadata['version']}\n\n" +
                           '\n\n'.join(p.read_text().strip() for p in files) + '\n')
        (root / 'THIRD_PARTY_NOTICES.md').write_text('\n'.join(notices))
        print('Updated ' + name + ' production dependency notices.')


if __name__ == '__main__':
    update()
