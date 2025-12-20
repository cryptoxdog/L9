import os
import subprocess
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uvicorn
import requests

# Load from environment
EXECUTOR_KEY = os.getenv("L9_EXECUTOR_API_KEY")
if not EXECUTOR_KEY:
    raise RuntimeError("L9_EXECUTOR_API_KEY not set")

MEMORY_HEALTH_URL = "http://127.0.0.1:8000/memory/stats"

# RESTRICTED command whitelist (READ-ONLY operations)
ALLOWED_SHELL_PREFIXES = [
    "journalctl",
    "systemctl status",
    "ls",
    "cat",
    "tail",
    "head",
    "df",
    "du",
    "ps",
    "grep",
    "curl",
]

app = FastAPI(title="L9 CTO Agent", version="1.0")

class ShellTask(BaseModel):
    type: Literal["shell"]
    command: str
    working_dir: Optional[str] = "/opt/l9"

class MemoryHealthTask(BaseModel):
    type: Literal["memory_health"]

class CompositeTask(BaseModel):
    type: str
    command: Optional[str] = None
    working_dir: Optional[str] = "/opt/l9"

def check_auth(authorization: str = Header(...)) -> None:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split(" ", 1)[1].strip()
    if token != EXECUTOR_KEY:
        raise HTTPException(status_code=403, detail="Invalid executor key")

def is_allowed_command(cmd: str) -> bool:
    stripped = cmd.strip()
    if not stripped:
        return False
    return any(stripped.startswith(prefix) for prefix in ALLOWED_SHELL_PREFIXES)

def run_shell(command: str, cwd: str = "/opt/l9") -> dict:
    if not is_allowed_command(command):
        raise HTTPException(
            status_code=400,
            detail=f"Command not allowed. Must start with: {', '.join(ALLOWED_SHELL_PREFIXES)}",
        )
    
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=30,  # Shorter timeout
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "Command timed out after 30s",
        }
    
    return {
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-2000:],
    }

def memory_health() -> dict:
    try:
        resp = requests.get(
            MEMORY_HEALTH_URL,
            headers={"Authorization": f"Bearer {EXECUTOR_KEY}"},
            timeout=10,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Memory health call failed: {e}")
    
    return {
        "status_code": resp.status_code,
        "body": resp.text,
    }

@app.get("/agent/health")
def agent_health():
    return {"status": "ok", "role": "cto_agent", "mode": "read_only"}

@app.post("/agent/exec")
def agent_exec(task: CompositeTask, authorization: str = Header(...)):
    check_auth(authorization)
    
    if task.type == "shell":
        if not task.command:
            raise HTTPException(status_code=400, detail="Missing command")
        result = run_shell(task.command, task.working_dir or "/opt/l9")
        return {"mode": "shell", "command": task.command, "result": result}
    
    if task.type == "memory_health":
        result = memory_health()
        return {"mode": "memory_health", "result": result}
    
    raise HTTPException(status_code=400, detail=f"Unsupported task type: {task.type}")

if __name__ == "__main__":
    uvicorn.run(
        "api.vps_executor:app",
        host="127.0.0.1",
        port=8100,
        reload=False,
        log_level="info",
    )
