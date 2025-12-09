# l/event_hooks_state_patch.py

from l.state_loader import load_identity

def on_directive(runtime, directive):
    identity = load_identity()
    
    runtime.EVENT_LOG.append({
        "event": "directive",
        "agent": identity["name"],
        "directive": directive
    })

