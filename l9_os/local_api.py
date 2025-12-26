"""
L9 Local API
Safe shell execution and file operations.
No shell injection - all commands validated.
"""

import subprocess
import shlex
import structlog
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

logger = structlog.get_logger(__name__)


class LocalAPI:
    """Safe local API for shell commands and file operations."""
    
    # Allowed commands whitelist (Phase 1 minimal set)
    ALLOWED_COMMANDS = {
        'ls', 'pwd', 'cat', 'head', 'tail', 'grep', 'find',
        'mkdir', 'rmdir', 'touch', 'cp', 'mv', 'rm',
        'python3', 'python', 'pip3', 'pip',
        'git', 'curl', 'wget'
    }
    
    # Blocked dangerous patterns
    BLOCKED_PATTERNS = [
        'rm -rf /', 'rm -rf ~', 'rm -rf *',
        'format', 'mkfs', 'dd if=', '> /dev/',
        'sudo rm', 'sudo format', 'sudo mkfs'
    ]
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.base_path = Path(settings.get("base_path", "/opt/l9"))
        self.timeout = settings.get("request_timeout", 30)
        
    def validate_command(self, cmd: str) -> bool:
        """Validate command against whitelist and blocked patterns."""
        # Check blocked patterns
        cmd_lower = cmd.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in cmd_lower:
                logger.warning(f"Blocked pattern detected: {pattern}")
                return False
        
        # Extract first command (before pipe or redirect)
        first_cmd = cmd.split()[0] if cmd.split() else ""
        if first_cmd not in self.ALLOWED_COMMANDS:
            logger.warning(f"Command not in whitelist: {first_cmd}")
            return False
        
        return True
    
    def execute_shell(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute shell command safely.
        Returns: {success: bool, output: str, error: str, exit_code: int}
        """
        if not self.validate_command(command):
            return {
                "success": False,
                "output": "",
                "error": "Command validation failed",
                "exit_code": -1
            }
        
        try:
            # Use shlex to safely parse command
            cmd_parts = shlex.split(command)
            cwd_path = Path(cwd) if cwd else self.base_path
            
            logger.info(f"Executing: {command} (cwd={cwd_path})")
            
            result = subprocess.run(
                cmd_parts,
                cwd=cwd_path,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {command}")
            return {
                "success": False,
                "output": "",
                "error": "Command execution timeout",
                "exit_code": -1
            }
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1
            }
    
    def read_file(self, file_path: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Read file safely.
        Returns: {success: bool, content: str, error: str}
        """
        try:
            path = Path(file_path)
            
            # Prevent path traversal
            if not path.resolve().is_relative_to(self.base_path.resolve()):
                return {
                    "success": False,
                    "content": "",
                    "error": "Path traversal blocked"
                }
            
            if not path.exists():
                return {
                    "success": False,
                    "content": "",
                    "error": "File not found"
                }
            
            with open(path, 'r') as f:
                if limit:
                    content = ''.join(f.readlines()[:limit])
                else:
                    content = f.read()
            
            return {
                "success": True,
                "content": content,
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"File read error: {e}")
            return {
                "success": False,
                "content": "",
                "error": str(e)
            }
    
    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write file safely.
        Returns: {success: bool, error: str}
        """
        try:
            path = Path(file_path)
            
            # Prevent path traversal
            if not path.resolve().is_relative_to(self.base_path.resolve()):
                return {
                    "success": False,
                    "error": "Path traversal blocked"
                }
            
            # Create parent directories
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                f.write(content)
            
            logger.info(f"File written: {file_path}")
            return {
                "success": True,
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"File write error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_directory(self, dir_path: str) -> Dict[str, Any]:
        """
        List directory contents.
        Returns: {success: bool, files: List[str], error: str}
        """
        try:
            path = Path(dir_path)
            
            # Prevent path traversal
            if not path.resolve().is_relative_to(self.base_path.resolve()):
                return {
                    "success": False,
                    "files": [],
                    "error": "Path traversal blocked"
                }
            
            if not path.exists():
                return {
                    "success": False,
                    "files": [],
                    "error": "Directory not found"
                }
            
            if not path.is_dir():
                return {
                    "success": False,
                    "files": [],
                    "error": "Not a directory"
                }
            
            files = [f.name for f in path.iterdir()]
            return {
                "success": True,
                "files": files,
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"Directory list error: {e}")
            return {
                "success": False,
                "files": [],
                "error": str(e)
            }

