"""
L Runtime Client - HTTP client for L to call L9 Runtime
"""
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RuntimeClient:
    """
    HTTP client for L (CTO) to communicate with L9 Runtime.
    
    Provides methods to:
    - Execute directives
    - Check health
    - Query module status
    - Get introspection data
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize runtime client.
        
        Args:
            base_url: Base URL of L9 Runtime API
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def execute_directive(self, directive: dict) -> dict:
        """
        Execute a directive on L9 Runtime.
        
        Args:
            directive: Command directive with 'command' and parameters
            
        Returns:
            Execution result from runtime
        """
        try:
            response = self.session.post(
                f"{self.base_url}/directive",
                json=directive,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Runtime client error: {e}")
            return {
                "success": False,
                "error": f"Runtime communication failed: {str(e)}"
            }
    
    def health_check(self) -> dict:
        """
        Check L9 Runtime health.
        
        Returns:
            Health status
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_modules(self) -> dict:
        """
        Get list of loaded modules.
        
        Returns:
            Module list
        """
        try:
            response = self.session.get(
                f"{self.base_url}/modules",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Module list failed: {e}")
            return {
                "modules": [],
                "error": str(e)
            }
    
    def get_introspection(self) -> dict:
        """
        Get runtime introspection data.
        
        Returns:
            Runtime status and metrics
        """
        try:
            response = self.session.get(
                f"{self.base_url}/introspection",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Introspection failed: {e}")
            return {
                "error": str(e)
            }

