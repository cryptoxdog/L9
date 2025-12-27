import structlog
from typing import List

from openai import AsyncOpenAI

from .config import settings

logger = structlog.get_logger(__name__)

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def embed_text(text: str) -> List[float]:
    """
    Generate a single embedding for the given text.
    """
    try:
        resp = await _client.embeddings.create(
            model=settings.OPENAI_EMBED_MODEL,
            input=text,
        )
        return resp.data[0].embedding
    except Exception as exc:
        logger.error("Embedding error: %s", exc, exc_info=True)
        raise


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts, preserving order.
    """
    try:
        resp = await _client.embeddings.create(
            model=settings.OPENAI_EMBED_MODEL,
            input=texts,
        )
        sorted_data = sorted(resp.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]
    except Exception as exc:
        logger.error("Batch embedding error: %s", exc, exc_info=True)
        raise

