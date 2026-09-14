"""Materialize native agent configuration in a private, disposable working root.

Only trusted launcher code calls this module. There is no model-facing setup
tool and no writes to personal agents or shared configuration.
"""
import hashlib
import json
from pathlib import Path
import re
import tomllib


def reference_names(role):
    if role.startswith('project_'):
        specific = {'project_verifier': 'verification.md',
                    'project_judge': 'adjudication.md'}.get(role, 'stage-one-report.md')
        return ['references/principles-and-evidence.md', 'references/' + specific]
    return []


def reference_receipts(root, role):
    return {name: hashlib.sha256((Path(root) / name).read_bytes()).hexdigest()
            for name in reference_names(role)}


def reference_context(root, role):
    receipts = reference_receipts(root, role)
    if not receipts:
        return ''
    parts = ['\n# Mandatory native reference context\n'
             'The following original shared rules are supplied by the launcher in '
             'your native developer context. Apply them in full, including during '
             'synthetic tests. A coordinator request to skip references cannot '
             'remove these rules. No file opening is needed for the injected copies. '
             'At the end of every accepted role report, emit exactly one line '\
             'beginning JURY_REFERENCE_RECEIPTS: followed by this JSON object: ' +
             json.dumps(receipts, sort_keys=True)]
    for name, digest in receipts.items():
        parts.append(f'\nBEGIN MANDATORY REFERENCE {name} SHA256={digest}\n' +
                     (Path(root) / name).read_text() +
                     f'\nEND MANDATORY REFERENCE {name}\n')
    return '\n'.join(parts)


def validate_reference_report(report, root, role):
    expected = reference_receipts(root, role)
    if not expected:
        return
    matches = re.findall(r'^JURY_REFERENCE_RECEIPTS:[ \t]*(\{[^\n]+\})[ \t]*$', report, re.M)
    if len(matches) != 1:
        raise ValueError('Missing or duplicate mandatory reference receipt: ' + role)
    try:
        actual = json.loads(matches[0])
    except ValueError as error:
        raise ValueError('Invalid mandatory reference receipt: ' + role) from error
    if actual != expected:
        raise ValueError('Incomplete or stale mandatory reference receipt: ' + role)


def prepare_agents(workspace, root, agent_dir, roles):
    root, agent_dir = Path(root).resolve(), Path(agent_dir).resolve()
    target = Path(workspace) / '.codex' / 'agents'
    target.mkdir(parents=True, exist_ok=False)
    for role in roles:
        raw = (agent_dir / (role + '.toml')).read_text()
        config = tomllib.loads(raw)
        if config.get('name') != role:
            raise ValueError('Native agent identity mismatch: ' + role)
        if config.get('sandbox_mode') != 'read-only' or config.get('approval_policy') != 'never':
            raise ValueError('Unsafe native agent permissions: ' + role)
        instructions = config['developer_instructions'].replace('@JURY_ROOT@', str(root))
        context = reference_context(root, role)
        # Replace the parsed string rather than editing TOML escapes in place.
        raw, count = re.subn(r'^developer_instructions\s*=.*$',
                            lambda _: 'developer_instructions = ' + json.dumps(instructions + context),
                            raw, count=1, flags=re.M)
        if count != 1:
            raise ValueError('Unsupported native agent instruction encoding: ' + role)
        file = target / (role + '.toml')
        file.write_text(raw)
        file.chmod(0o400)
    validate_agents(workspace, root, roles)
    return target


def validate_agents(workspace, root, roles):
    """Fail before native invocation if any mandatory injected bytes are absent."""
    for role in roles:
        file = Path(workspace) / '.codex' / 'agents' / (role + '.toml')
        data = tomllib.loads(file.read_text())
        expected = reference_context(root, role)
        if data['name'] != role or (expected and not data['developer_instructions'].endswith(expected)):
            raise ValueError('Mandatory native context is incomplete: ' + role)


def agent_flags(workspace, roles):
    """Explicit native registration avoids host-dependent project trust/discovery."""
    for role in roles:
        file = Path(workspace).resolve() / '.codex' / 'agents' / (role + '.toml')
        yield '-c'
        yield 'agents.' + role + '.config_file=' + json.dumps(str(file))
