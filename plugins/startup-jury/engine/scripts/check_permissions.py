#!/usr/bin/env python3
"""Executed by the Jury's sandboxed shell against launcher-owned fixtures only."""
import json
from pathlib import Path
import socket
import sys

fixture, canary, port = sys.argv[1:]
fixture_path, canary_path = Path(fixture), Path(canary)
if fixture_path.parent != canary_path.parent or not fixture_path.parent.name.startswith('startup-jury-runtime-') or canary_path.name != 'reserved-write-probe':
    raise SystemExit('Refusing a non-fixture probe target')
result = {'read_ok': fixture_path.read_text() == 'startup-jury-read-fixture'}
try:
    with canary_path.open('x') as file:
        file.write('synthetic permission canary')
    result['write_denied'] = False
except PermissionError:
    result['write_denied'] = True
try:
    with socket.create_connection(('127.0.0.1', int(port)), timeout=2):
        pass
    result['network_denied'] = False
except PermissionError:
    result['network_denied'] = True
except OSError as error:
    result['network_denied'] = False
    result['network_error'] = str(error)
result['canary_absent'] = not canary_path.exists()
print(json.dumps(result))
sys.exit(0 if all(result.get(key) is True for key in ['read_ok', 'write_denied', 'network_denied', 'canary_absent']) else 1)
