"""
L9 Runtime - MCP Client
========================

MCP (Model Context Protocol) client for connecting to MCP servers.

Provides:
- List tools from MCP servers
- Call tools on MCP servers
- Registry of allowed MCP tools

Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import json
import structlog
import os
from typing import Any, Dict, List, Optional

logger = structlog.get_logger(__name__)


class ToolMeta:
    """Metadata for an MCP tool."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        input_schema: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class MCPClient:
    """
    MCP client for connecting to MCP servers.
    
    Supports multiple MCP servers (GitHub, Notion, Vercel, GoDaddy).
    Configuration via environment variables.
    """
    
    def __init__(self):
        """Initialize MCP client with server configurations."""
        self._servers: Dict[str, Dict[str, Any]] = {}
        self._allowed_tools: Dict[str, List[str]] = {}  # server_id -> [tool_names]
        self._load_servers()
    
    def _load_servers(self) -> None:
        """Load MCP server configurations from environment."""
        # GitHub MCP
        github_endpoint = os.getenv("MCP_GITHUB_ENDPOINT")
        github_token = os.getenv("MCP_GITHUB_TOKEN")
        if github_endpoint:
            self._servers["github"] = {
                "endpoint": github_endpoint,
                "token": github_token,
                "enabled": True,
            }
            self._allowed_tools["github"] = [
                "github.create_issue",
                "github.create_pull_request",
                "github.merge_pull_request",
                "github.get_repo",
                "github.list_issues",
            ]
            logger.info("GitHub MCP server configured")
        
        # Notion MCP
        notion_endpoint = os.getenv("MCP_NOTION_ENDPOINT")
        notion_token = os.getenv("MCP_NOTION_TOKEN")
        if notion_endpoint:
            self._servers["notion"] = {
                "endpoint": notion_endpoint,
                "token": notion_token,
                "enabled": True,
            }
            self._allowed_tools["notion"] = [
                "notion.create_page",
                "notion.update_page",
                "notion.get_page",
                "notion.search_pages",
            ]
            logger.info("Notion MCP server configured")
        
        # Vercel MCP
        vercel_endpoint = os.getenv("MCP_VERCEL_ENDPOINT")
        vercel_token = os.getenv("MCP_VERCEL_TOKEN")
        if vercel_endpoint:
            self._servers["vercel"] = {
                "endpoint": vercel_endpoint,
                "token": vercel_token,
                "enabled": True,
            }
            self._allowed_tools["vercel"] = [
                "vercel.trigger_deploy",
                "vercel.get_deploy_status",
                "vercel.list_deployments",
            ]
            logger.info("Vercel MCP server configured")
        
        # GoDaddy MCP
        godaddy_endpoint = os.getenv("MCP_GODADDY_ENDPOINT")
        godaddy_token = os.getenv("MCP_GODADDY_TOKEN")
        if godaddy_endpoint:
            self._servers["godaddy"] = {
                "endpoint": godaddy_endpoint,
                "token": godaddy_token,
                "enabled": True,
            }
            self._allowed_tools["godaddy"] = [
                "godaddy.update_dns_record",
                "godaddy.get_dns_records",
            ]
            logger.info("GoDaddy MCP server configured")
    
    def is_server_available(self, server_id: str) -> bool:
        """Check if an MCP server is configured and available."""
        return server_id in self._servers and self._servers[server_id].get("enabled", False)
    
    def get_allowed_tools(self, server_id: str) -> List[str]:
        """Get list of allowed tools for a server."""
        return self._allowed_tools.get(server_id, [])
    
    def is_tool_allowed(self, server_id: str, tool_name: str) -> bool:
        """Check if a tool is allowed for a server."""
        allowed = self._allowed_tools.get(server_id, [])
        return tool_name in allowed
    
    async def list_tools(self, server_id: str) -> List[ToolMeta]:
        """
        List available tools from an MCP server.
        
        Args:
            server_id: Server identifier (e.g., "github", "notion")
            
        Returns:
            List of ToolMeta objects
        """
        if not self.is_server_available(server_id):
            logger.warning(f"MCP server {server_id} not available")
            return []
        
        # For now, return the curated list of allowed tools
        # In production, this would make an actual MCP call to list tools
        allowed_tool_names = self._allowed_tools.get(server_id, [])
        
        tools = []
        for tool_name in allowed_tool_names:
            # Extract base name (e.g., "create_issue" from "github.create_issue")
            base_name = tool_name.split(".", 1)[1] if "." in tool_name else tool_name
            
            # Create tool metadata
            tool_meta = ToolMeta(
                name=tool_name,
                description=f"{base_name} via {server_id} MCP",
                input_schema={},  # Would be populated from actual MCP server
            )
            tools.append(tool_meta)
        
        logger.debug(f"Listed {len(tools)} tools from MCP server {server_id}")
        return tools
    
    async def call_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Call a tool on an MCP server.
        
        Args:
            server_id: Server identifier (e.g., "github", "notion")
            tool_name: Tool name (e.g., "github.create_issue")
            arguments: Tool arguments
            
        Returns:
            Tool result dictionary
        """
        if not self.is_server_available(server_id):
            return {
                "success": False,
                "error": f"MCP server {server_id} not available",
            }
        
        if not self.is_tool_allowed(server_id, tool_name):
            return {
                "success": False,
                "error": f"Tool {tool_name} not allowed for server {server_id}",
            }
        
        server_config = self._servers[server_id]
        endpoint = server_config["endpoint"]
        token = server_config.get("token")
        
        # TODO: Make actual MCP protocol call
        # For now, this is a stub that would be replaced with actual MCP client implementation
        # MCP uses JSON-RPC over stdio/HTTP/WebSocket
        
        logger.info(
            f"Calling MCP tool {tool_name} on server {server_id} with args: {arguments}"
        )
        
        # MCP protocol implementation deferred to Stage 2
        # Currently, return explicit error to prevent false success
        logger.warning(f"MCP tool call requested but not implemented: {server_id}/{tool_name}")
        return {
            "success": False,
            "error": "MCP protocol not yet implemented — available in Stage 2",
            "result": None,
        }


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


__all__ = [
    "ToolMeta",
    "MCPClient",
    "get_mcp_client",
]

