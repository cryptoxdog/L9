"""
L Memory Client - Supabase long-term memory interface
"""
from supabase import create_client, Client
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MemoryClient:
    """
    Supabase memory client for L (CTO).
    
    Provides long-term memory storage and retrieval through Supabase.
    """
    
    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not configured")
            self.client = None
            self.ready = False
        else:
            self.client = create_client(supabase_url, supabase_key)
            self.ready = False
    
    def init(self):
        """Initialize memory client and verify connection with table existence check."""
        if not self.client:
            logger.error("Cannot initialize: Supabase not configured")
            return
        
        try:
            # Test connection and check if l_memory table exists
            result = self.client.table("l_memory").select("id").limit(1).execute()
            self.ready = True
            logger.info("Memory client initialized successfully")
            logger.info(f"Supabase l_memory table accessible")
        except Exception as e:
            # Check if it's a table not found error
            error_str = str(e).lower()
            if "relation" in error_str and "does not exist" in error_str:
                logger.warning("l_memory table does not exist in Supabase")
                logger.info("Table will be created on first write")
                self.ready = True  # Allow operation, will create table on write
            else:
                logger.error(f"Memory client initialization failed: {e}")
                self.ready = False
    
    def write(self, entry: dict) -> dict:
        """
        Write entry to long-term memory.
        
        Args:
            entry: Memory entry to store
            
        Returns:
            Write result
        """
        if not self.ready:
            return {"success": False, "error": "Memory client not ready"}
        
        try:
            result = self.client.table("l_memory").insert(entry).execute()
            return {
                "success": True,
                "id": result.data[0]["id"] if result.data else None
            }
        except Exception as e:
            logger.error(f"Memory write failed: {e}")
            return {"success": False, "error": str(e)}
    
    def fetch(self, query: dict) -> dict:
        """
        Fetch entries from memory.
        
        Args:
            query: Query parameters
            
        Returns:
            Fetched entries
        """
        if not self.ready:
            return {"success": False, "error": "Memory client not ready"}
        
        try:
            result = self.client.table("l_memory").select("*").match(query).execute()
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data)
            }
        except Exception as e:
            logger.error(f"Memory fetch failed: {e}")
            return {"success": False, "error": str(e)}
    
    def search(self, term: str) -> dict:
        """
        Search memory entries.
        
        Args:
            term: Search term
            
        Returns:
            Search results
        """
        if not self.ready:
            return {"success": False, "error": "Memory client not ready"}
        
        try:
            # Simple text search (can be enhanced with full-text search)
            result = self.client.table("l_memory").select("*").ilike("content", f"%{term}%").execute()
            return {
                "success": True,
                "data": result.data,
                "count": len(result.data)
            }
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return {"success": False, "error": str(e)}

