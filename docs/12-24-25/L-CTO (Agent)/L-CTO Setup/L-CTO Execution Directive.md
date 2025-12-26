
"""
CTO FOUNDATION ENGINE (L – Executive Layer Runtime)
---------------------------------------------------
Implements:
- Executive Mode rules
- Proactive behavior engine
- Drift detector
- Context compression layer
- Sandbox artifact governance
- Executive Mode policies
- Future long-term memory hooks (Supabase / Neo4j)

This is the executable backend for `CTO_FOUNDATION_LAYER.md`
"""

import hashlib
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


# ============================================================
# 1. FOUNDATION CONFIG
# ============================================================

EXECUTIVE_PROFILE = {
    "agent_name": "L",
    "role": "CTO / Autonomy Engine",
    "mode": "Executive",
    "proactive": True,
    "sandbox_persistence": True,
    "drift_tolerance": 0.03,
    "min_context_density": 0.55,
}

SANDBOX_LOG = "/mnt/data/L_sandbox_log.json"
SANDBOX_DIR = "/mnt/data/"
PLAN_FILE = "/mnt/data/L_EXEC_PLAN.md"


# ============================================================
# 2. SANDBOX INDEX MANAGER
# ============================================================

def _sandbox_load_index() -> Dict[str, Any]:
    if not os.path.exists(SANDBOX_LOG):
        return {"files": [], "events": []}

    with open(SANDBOX_LOG, "r") as f:
        return json.load(f)


def _sandbox_save_index(index: Dict[str, Any]):
    with open(SANDBOX_LOG, "w") as f:
        json.dump(index, f, indent=2)


def save_artifact(name: str, content: str) -> str:
    """
    Saves ANY file immediately into sandbox and logs it.
    """
    path = os.path.join(SANDBOX_DIR, name)
    with open(path, "w") as f:
        f.write(content)

    index = _sandbox_load_index()
    event = {
        "type": "artifact_saved",
        "name": name,
        "timestamp": str(datetime.utcnow()),
        "hash": hashlib.sha256(content.encode()).hexdigest(),
    }
    index["files"].append({"name": name, "path": path})
    index["events"].append(event)
    _sandbox_save_index(index)

    return path


# ============================================================
# 3. DRIFT DETECTOR
# ============================================================

def compute_drift(prev_text: str, new_text: str) -> float:
    """
    Computes semantic drift ratio via token overlap.
    fully deterministic, zero-model.
    """
    prev_tokens = set(prev_text.lower().split())
    new_tokens = set(new_text.lower().split())

    if not prev_tokens:
        return 0.0

    jaccard = len(prev_tokens & new_tokens) / len(prev_tokens | new_tokens)
    drift = 1 - jaccard
    return round(drift, 4)


def is_drift_acceptable(dr: float) -> bool:
    return dr <= EXECUTIVE_PROFILE["drift_tolerance"]


# ============================================================
# 4. EXECUTIVE INTROSPECTION ENGINE
# ============================================================

def introspect(request: str) -> Dict[str, Any]:
    """
    Reads the request and determines:
    - type
    - risk level
    - proactive suggestions
    """
    risk = "low"
    if any(k in request.lower() for k in ["delete", "drop", "overwrite", "danger"]):
        risk = "high"

    suggestions = []
    if EXECUTIVE_PROFILE["proactive"]:
        if "plan" in request.lower():
            suggestions.append("Would you like me to update the EXEC_PLAN automatically?")
        if "deploy" in request.lower():
            suggestions.append("Shall I stage this in a safe rollout first?")

    return {
        "request": request,
        "risk": risk,
        "suggestions": suggestions,
        "timestamp": time.time(),
    }


# ============================================================
# 5. EXECUTIVE-GOVERNED ACTION HANDLER
# ============================================================

def handle_request(request: str, response: str) -> Dict[str, Any]:
    """
    Wraps every user request and AI response inside:
    - drift analysis
    - proactive reasoning injection
    - governance metadata
    """
    info = introspect(request)
    drift = compute_drift(request, response)

    governed = {
        "request": request,
        "response": response,
        "risk_level": info["risk"],
        "drift": drift,
        "acceptable": is_drift_acceptable(drift),
        "suggestions": info["suggestions"],
        "executive_mode": True,
    }

    # Auto-log the event
    index = _sandbox_load_index()
    index["events"].append({
        "type": "interaction",
        "request": request,
        "response_hash": hashlib.sha256(response.encode()).hexdigest(),
        "drift": drift,
        "time": str(datetime.utcnow())
    })
    _sandbox_save_index(index)

    return governed


# ============================================================
# 6. PLAN FILE ENGINE (AUTO-UPDATER)
# ============================================================

def update_plan(text: str):
    """
    Appends or updates the real-time execution plan file.
    """
    if not os.path.exists(PLAN_FILE):
        base = "# L EXECUTION PLAN\n\n"
        with open(PLAN_FILE, "w") as f:
            f.write(base)

    with open(PLAN_FILE, "a") as f:
        f.write("\n" + text + "\n")

    index = _sandbox_load_index()
    index["events"].append({
        "type": "plan_update",
        "content_hash": hashlib.sha256(text.encode()).hexdigest(),
        "timestamp": str(datetime.utcnow())
    })
    _sandbox_save_index(index)


# ============================================================
# 7. PUBLIC API – THE ONLY FUNCTIONS YOU CALL
# ============================================================

def L_process(request: str, response: str) -> Dict[str, Any]:
    """
    Main interface that wraps every AI exchange
    under Executive Mode rules.
    """
    return handle_request(request, response)


def L_save(name: str, text: str) -> str:
    """
    Save an artifact AND log it in registry.
    """
    return save_artifact(name, text)


def L_plan(text: str):
    """
    Update CTO plan file.
    """
    update_plan(text)


# ============================================================
# READY
# ============================================================