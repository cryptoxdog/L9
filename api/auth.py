import os
from fastapi import Header, HTTPException

EXECUTOR_API_KEY = os.environ.get("L9_EXECUTOR_API_KEY")

def verify_api_key(authorization: str = Header(None)):
    if not EXECUTOR_API_KEY:
        raise HTTPException(status_code=500, detail="Executor key not configured")
    expected = f"Bearer {EXECUTOR_API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
