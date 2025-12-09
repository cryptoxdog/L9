import hmac, hashlib
from fastapi import HTTPException, status
from .config import settings


def verify_agent_token(token: str):
    if token != settings.agent_auth_token:
        raise HTTPException(status_code=401, detail="Invalid agent token")


def sign_payload(payload: bytes) -> str:
    return hmac.new(
        key=settings.hmac_secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()


def verify_signature(payload: bytes, signature: str) -> bool:
    return hmac.compare_digest(sign_payload(payload), signature)

