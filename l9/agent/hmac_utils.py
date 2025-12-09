import hmac, hashlib
from .config import settings


def sign(payload: bytes) -> str:
    return hmac.new(
        settings.agent_auth_token.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()


def verify(payload: bytes, signature: str) -> bool:
    return hmac.compare_digest(sign(payload), signature)

