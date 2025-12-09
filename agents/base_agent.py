"""
L9 Agents - Base Agent
======================

Abstract base class for all L9 agents.

Provides:
- LLM client management
- Message handling
- Memory integration
- Standard interfaces
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent roles in the system."""
    ARCHITECT_PRIMARY = "architect_primary"
    ARCHITECT_CHALLENGER = "architect_challenger"
    CODER_PRIMARY = "coder_primary"
    CODER_SECONDARY = "coder_secondary"
    QA = "qa"
    REFLECTION = "reflection"


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    api_key: Optional[str] = None
    model: str = "gpt-4o"
    temperature: float = 0.3
    max_tokens: int = 4000
    timeout_seconds: int = 120
    retry_count: int = 3
    system_prompt_override: Optional[str] = None


@dataclass
class AgentMessage:
    """A message to/from an agent."""
    message_id: UUID = field(default_factory=uuid4)
    role: str = "user"  # system, user, assistant
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, str]:
        """Convert to OpenAI message format."""
        return {"role": self.role, "content": self.content}


@dataclass
class AgentResponse:
    """Response from an agent."""
    response_id: UUID = field(default_factory=uuid4)
    agent_id: str = ""
    content: str = ""
    structured_output: Optional[dict[str, Any]] = None
    tokens_used: int = 0
    duration_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "response_id": str(self.response_id),
            "agent_id": self.agent_id,
            "content": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "success": self.success,
            "tokens_used": self.tokens_used,
            "duration_ms": self.duration_ms,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all L9 agents.
    
    Subclasses must implement:
    - get_system_prompt(): Return the agent's system prompt
    - run(): Execute the agent's primary function
    """
    
    agent_role: AgentRole = AgentRole.REFLECTION
    agent_name: str = "base_agent"
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
    ):
        """
        Initialize the agent.
        
        Args:
            agent_id: Unique identifier (auto-generated if not provided)
            config: Agent configuration
        """
        self._agent_id = agent_id or f"{self.agent_name}_{uuid4().hex[:8]}"
        self._config = config or AgentConfig()
        self._client: Optional[AsyncOpenAI] = None
        self._conversation_history: list[AgentMessage] = []
        self._initialized = False
        
        logger.info(f"Initialized {self.agent_name} with id={self._agent_id}")
    
    @property
    def agent_id(self) -> str:
        """Get agent ID."""
        return self._agent_id
    
    @property
    def config(self) -> AgentConfig:
        """Get agent configuration."""
        return self._config
    
    def _ensure_client(self) -> AsyncOpenAI:
        """Ensure OpenAI client is initialized."""
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self._config.api_key)
        return self._client
    
    # ==========================================================================
    # Abstract Methods
    # ==========================================================================
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the agent's system prompt.
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    async def run(self, task: dict[str, Any], context: Optional[dict[str, Any]] = None) -> AgentResponse:
        """
        Execute the agent's primary function.
        
        Args:
            task: Task specification
            context: Optional execution context
            
        Returns:
            AgentResponse with result
        """
        pass
    
    # ==========================================================================
    # LLM Interaction
    # ==========================================================================
    
    async def call_llm(
        self,
        messages: list[AgentMessage],
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> AgentResponse:
        """
        Call the LLM with messages.
        
        Args:
            messages: List of messages
            temperature: Override temperature
            json_mode: If True, request JSON output
            
        Returns:
            AgentResponse
        """
        client = self._ensure_client()
        start_time = datetime.utcnow()
        
        # Build message list with system prompt
        api_messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ]
        api_messages.extend([m.to_dict() for m in messages])
        
        try:
            kwargs: dict[str, Any] = {
                "model": self._config.model,
                "messages": api_messages,
                "temperature": temperature if temperature is not None else self._config.temperature,
                "max_tokens": self._config.max_tokens,
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = await client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Parse JSON if in json_mode
            structured_output = None
            if json_mode:
                try:
                    structured_output = json.loads(content)
                except json.JSONDecodeError:
                    structured_output = self._extract_json(content)
            
            return AgentResponse(
                agent_id=self._agent_id,
                content=content,
                structured_output=structured_output,
                tokens_used=tokens,
                duration_ms=duration_ms,
                success=True,
            )
            
        except Exception as e:
            logger.error(f"LLM call failed for {self._agent_id}: {e}")
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return AgentResponse(
                agent_id=self._agent_id,
                content="",
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )
    
    async def call_llm_json(
        self,
        prompt: str,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Call LLM and get JSON response.
        
        Args:
            prompt: User prompt
            context: Optional context to include
            
        Returns:
            Parsed JSON dict
        """
        full_prompt = prompt
        if context:
            full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        messages = [AgentMessage(role="user", content=full_prompt)]
        response = await self.call_llm(messages, json_mode=True)
        
        return response.structured_output or {}
    
    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract JSON from text that may contain extra content."""
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        
        logger.warning(f"Could not extract JSON from response")
        return {}
    
    # ==========================================================================
    # Conversation Management
    # ==========================================================================
    
    def add_message(self, message: AgentMessage) -> None:
        """Add a message to conversation history."""
        self._conversation_history.append(message)
    
    def get_history(self) -> list[AgentMessage]:
        """Get conversation history."""
        return self._conversation_history.copy()
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self._conversation_history.clear()
    
    def get_recent_messages(self, count: int = 10) -> list[AgentMessage]:
        """Get recent messages from history."""
        return self._conversation_history[-count:]
    
    # ==========================================================================
    # Memory Integration
    # ==========================================================================
    
    def to_packet_payload(self, response: AgentResponse) -> dict[str, Any]:
        """
        Convert response to memory packet payload.
        
        Args:
            response: Agent response
            
        Returns:
            Payload for PacketEnvelopeIn
        """
        return {
            "kind": "agent_response",
            "agent_id": self._agent_id,
            "agent_role": self.agent_role.value,
            "response_id": str(response.response_id),
            "success": response.success,
            "tokens_used": response.tokens_used,
            "duration_ms": response.duration_ms,
            "content_length": len(response.content),
        }
    
    # ==========================================================================
    # Utility Methods
    # ==========================================================================
    
    def format_user_message(self, content: str) -> AgentMessage:
        """Create a user message."""
        return AgentMessage(role="user", content=content)
    
    def format_assistant_message(self, content: str) -> AgentMessage:
        """Create an assistant message."""
        return AgentMessage(role="assistant", content=content)
    
    async def health_check(self) -> dict[str, Any]:
        """Check agent health."""
        try:
            response = await self.call_llm(
                [AgentMessage(role="user", content="Reply with 'ok'")],
                temperature=0,
            )
            return {
                "status": "healthy" if response.success else "unhealthy",
                "agent_id": self._agent_id,
                "model": self._config.model,
                "error": response.error,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "agent_id": self._agent_id,
                "error": str(e),
            }

