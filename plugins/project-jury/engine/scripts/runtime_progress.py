"""Allowlisted operational metadata only; never retain runtime text or reasoning."""
import json
from pathlib import Path
import time

ITEM_TYPES = {'agent_message', 'command_execution', 'web_search', 'collab_tool_call', 'mcp_tool_call', 'error'}
TOOLS = {'spawn_agent', 'send_input', 'wait', 'close_agent'}
STATUSES = {'pending_init', 'running', 'interrupted', 'completed', 'errored', 'shutdown', 'not_found'}


class RunProgress:
    def __init__(self, path):
        self.path = Path(path)
        self.seen = set()
        self.agents = {}
        self.value = {'event_count': 0, 'last_event_at': time.time(),
                      'last_activity': 'starting', 'item_counts': {},
                      'collaboration_counts': {}, 'agent_counts': {}}
        self.save()

    def update(self, event):
        self.value['event_count'] += 1
        self.value['last_event_at'] = time.time()
        kind = event.get('type')
        if kind in {'thread.started', 'turn.started', 'turn.completed', 'turn.failed', 'error'}:
            self.value['last_activity'] = kind
        item = event.get('item', {})
        if not isinstance(item, dict): item = {}
        item_type = item.get('type')
        if kind in {'item.started', 'item.completed'} and item_type in ITEM_TYPES:
            self.value['last_activity'] = item_type
            item_id = item.get('id')
            key = (item_type, item_id if isinstance(item_id,str) else self.value['event_count'])
            if key not in self.seen:
                self.seen.add(key)
                counts = self.value['item_counts']
                counts[item_type] = counts.get(item_type, 0) + 1
                tool = item.get('tool')
                if item_type == 'collab_tool_call' and tool in TOOLS:
                    counts = self.value['collaboration_counts']
                    counts[tool] = counts.get(tool, 0) + 1
            if item_type == 'collab_tool_call':
                states = item.get('agents_states', {})
                for agent_id, state in (states.items() if isinstance(states,dict) else []):
                    if isinstance(state,dict) and state.get('status') in STATUSES:
                        self.agents[agent_id] = state['status']
                self.value['agent_counts'] = {status: list(self.agents.values()).count(status)
                                             for status in STATUSES if status in self.agents.values()}
        self.save()

    def save(self):
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.value))
        temp.chmod(0o600)
        temp.replace(self.path)
