"""
L9 Research Factory - Tool Wrappers
Version: 1.0.0

Concrete tool implementations for research.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx

from config.research_settings import get_research_settings

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all tools."""
    
    @abstractmethod
    async def execute(self, args: dict[str, Any]) -> Any:
        """
        Execute the tool.
        
        Args:
            args: Tool arguments
            
        Returns:
            Tool result
        """
        pass


class PerplexityTool(BaseTool):
    """
    Perplexity AI search tool.
    
    Uses Perplexity API for web search and synthesis.
    Requires PERPLEXITY_API_KEY environment variable.
    """
    
    PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
    
    def __init__(self):
        """Initialize Perplexity tool."""
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from settings."""
        try:
            settings = get_research_settings()
            return settings.perplexity_api_key
        except Exception:
            return None
    
    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        Execute Perplexity search.
        
        Args:
            args: {"query": str} - The search query
            
        Returns:
            {"result": str, "sources": list} - Search result and sources
        """
        query = args.get("query", "")
        if not query:
            return {"result": "No query provided", "sources": []}
        
        api_key = self._get_api_key()
        if not api_key:
            logger.warning("Perplexity API key not configured, using mock response")
            return {
                "result": f"[Mock] Research results for: {query}",
                "sources": ["mock://source1", "mock://source2"],
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.PERPLEXITY_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful research assistant. Provide detailed, accurate information with sources.",
                            },
                            {
                                "role": "user",
                                "content": query,
                            },
                        ],
                    },
                    timeout=60.0,
                )
                
                response.raise_for_status()
                data = response.json()
                
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                citations = data.get("citations", [])
                
                return {
                    "result": content,
                    "sources": citations,
                }
                
        except Exception as e:
            logger.error(f"Perplexity search failed: {e}")
            return {
                "result": f"Search failed: {str(e)}",
                "sources": [],
                "error": str(e),
            }


class HTTPTool(BaseTool):
    """
    Generic HTTP request tool.
    
    Makes HTTP requests to external APIs.
    """
    
    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        Execute HTTP request.
        
        Args:
            args: {
                "url": str,
                "method": str (default "GET"),
                "headers": dict (optional),
                "body": dict (optional),
            }
            
        Returns:
            {"status": int, "body": str/dict}
        """
        url = args.get("url", "")
        method = args.get("method", "GET").upper()
        headers = args.get("headers", {})
        body = args.get("body")
        
        if not url:
            return {"status": 400, "body": "No URL provided"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body if body else None,
                    timeout=30.0,
                )
                
                # Try to parse JSON
                try:
                    body_data = response.json()
                except Exception:
                    body_data = response.text
                
                return {
                    "status": response.status_code,
                    "body": body_data,
                }
                
        except Exception as e:
            logger.error(f"HTTP request failed: {e}")
            return {
                "status": 500,
                "body": str(e),
                "error": str(e),
            }


class MockSearchTool(BaseTool):
    """
    Mock search tool for testing.
    
    Returns deterministic mock results without API calls.
    """
    
    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        Execute mock search.
        
        Args:
            args: {"query": str}
            
        Returns:
            Mock search results
        """
        query = args.get("query", "unknown query")
        
        # Generate deterministic mock results
        mock_results = {
            "result": (
                f"Mock research findings for '{query}':\n\n"
                f"1. Key Finding: This is a mock result for testing purposes.\n"
                f"2. Supporting Evidence: The query '{query}' was processed by the mock search tool.\n"
                f"3. Conclusion: Mock search provides deterministic results for testing.\n"
            ),
            "sources": [
                "https://mock.example.com/result1",
                "https://mock.example.com/result2",
                "https://mock.example.com/result3",
            ],
            "confidence": 0.9,
            "is_mock": True,
        }
        
        logger.debug(f"Mock search executed for: {query[:50]}")
        return mock_results

