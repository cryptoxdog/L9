#!/usr/bin/env python3
"""
L9 Mac Agent
Executes tasks sent from VPS on macOS workstation.
Supports GUI automation, shell commands, browser automation, and AppleScript.
"""

import os
import sys
import json
import time
import logging
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Automation libraries (optional imports)
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("PyAutoGUI not available - GUI automation disabled")

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available - browser automation disabled")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class MacAgent:
    """Mac Agent that executes tasks from VPS."""
    
    def __init__(
        self,
        vps_url: str = "http://localhost:8000",
        auth_token: str = "",
        poll_interval: int = 5
    ):
        self.vps_url = vps_url.rstrip('/')
        self.auth_token = auth_token
        self.poll_interval = poll_interval
        self.running = False
        self.playwright_browser: Optional[Browser] = None
        
        # Initialize Playwright if available
        if PLAYWRIGHT_AVAILABLE:
            self.playwright = sync_playwright().start()
        else:
            self.playwright = None
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to VPS."""
        url = f"{self.vps_url}{endpoint}"
        headers = {}
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                logger.error(f"Unsupported method: {method}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
    
    def poll_for_tasks(self) -> Optional[Dict]:
        """Poll VPS for pending tasks."""
        return self._make_request("/agent/tasks/poll", method="POST", data={"agent_id": "mac"})
    
    def send_result(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Send task execution result back to VPS."""
        data = {
            "task_id": task_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = self._make_request("/agent/tasks/result", method="POST", data=data)
        return response is not None and response.get("success", False)
    
    def execute_shell(self, command: str, cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
        """Execute shell command safely."""
        try:
            logger.info(f"Executing shell: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Command timeout",
                "exit_code": -1
            }
        except Exception as e:
            logger.error(f"Shell execution error: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1
            }
    
    def execute_gui(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GUI automation action."""
        if not PYAUTOGUI_AVAILABLE:
            return {
                "success": False,
                "error": "PyAutoGUI not available"
            }
        
        try:
            if action == "click":
                x = params.get("x")
                y = params.get("y")
                pyautogui.click(x, y)
                return {"success": True, "message": f"Clicked at ({x}, {y})"}
            
            elif action == "type":
                text = params.get("text", "")
                pyautogui.write(text)
                return {"success": True, "message": f"Typed: {text}"}
            
            elif action == "screenshot":
                filename = params.get("filename", f"screenshot_{int(time.time())}.png")
                screenshot = pyautogui.screenshot(filename)
                return {"success": True, "filename": filename}
            
            elif action == "move":
                x = params.get("x")
                y = params.get("y")
                pyautogui.moveTo(x, y)
                return {"success": True, "message": f"Moved to ({x}, {y})"}
            
            else:
                return {"success": False, "error": f"Unknown GUI action: {action}"}
                
        except Exception as e:
            logger.error(f"GUI execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_applescript(self, script: str) -> Dict[str, Any]:
        """Execute AppleScript command."""
        try:
            logger.info(f"Executing AppleScript: {script[:50]}...")
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "exit_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "AppleScript timeout",
                "exit_code": -1
            }
        except Exception as e:
            logger.error(f"AppleScript execution error: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1
            }
    
    def execute_browser(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute browser automation action."""
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "success": False,
                "error": "Playwright not available"
            }
        
        try:
            if not self.playwright_browser:
                # Launch browser on first use
                self.playwright_browser = self.playwright.chromium.launch(headless=False)
            
            context = self.playwright_browser.new_context()
            page = context.new_page()
            
            if action == "navigate":
                url = params.get("url", "")
                page.goto(url)
                return {"success": True, "url": url}
            
            elif action == "click":
                selector = params.get("selector", "")
                page.click(selector)
                return {"success": True, "selector": selector}
            
            elif action == "fill":
                selector = params.get("selector", "")
                text = params.get("text", "")
                page.fill(selector, text)
                return {"success": True, "selector": selector}
            
            elif action == "screenshot":
                filename = params.get("filename", f"browser_{int(time.time())}.png")
                page.screenshot(path=filename)
                return {"success": True, "filename": filename}
            
            elif action == "evaluate":
                script = params.get("script", "")
                result = page.evaluate(script)
                return {"success": True, "result": result}
            
            else:
                return {"success": False, "error": f"Unknown browser action: {action}"}
            
        except Exception as e:
            logger.error(f"Browser execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task based on task type."""
        task_type = task.get("type", "")
        task_id = task.get("id", "")
        payload = task.get("payload", {})
        
        logger.info(f"Executing task {task_id} of type {task_type}")
        
        if task_type == "shell":
            command = payload.get("command", "")
            cwd = payload.get("cwd")
            timeout = payload.get("timeout", 30)
            result = self.execute_shell(command, cwd=cwd, timeout=timeout)
        
        elif task_type == "gui":
            action = payload.get("action", "")
            params = payload.get("params", {})
            result = self.execute_gui(action, params)
        
        elif task_type == "applescript":
            script = payload.get("script", "")
            result = self.execute_applescript(script)
        
        elif task_type == "browser":
            action = payload.get("action", "")
            params = payload.get("params", {})
            result = self.execute_browser(action, params)
        
        else:
            result = {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
        
        return result
    
    def run(self):
        """Main agent loop - polls for tasks and executes them."""
        logger.info("Starting Mac Agent...")
        logger.info(f"VPS URL: {self.vps_url}")
        logger.info(f"Poll interval: {self.poll_interval}s")
        
        self.running = True
        
        while self.running:
            try:
                # Poll for tasks
                task_data = self.poll_for_tasks()
                
                if task_data and task_data.get("task"):
                    task = task_data["task"]
                    task_id = task.get("id", "")
                    
                    # Execute task
                    result = self.execute_task(task)
                    
                    # Send result back
                    self.send_result(task_id, result)
                    
                    logger.info(f"Task {task_id} completed: success={result.get('success', False)}")
                
                # Sleep before next poll
                time.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Agent loop error: {e}", exc_info=True)
                time.sleep(self.poll_interval)
        
        # Cleanup
        self.shutdown()
    
    def shutdown(self):
        """Clean shutdown."""
        logger.info("Shutting down Mac Agent...")
        self.running = False
        
        if self.playwright_browser:
            self.playwright_browser.close()
        
        if self.playwright:
            self.playwright.stop()
        
        logger.info("Shutdown complete")


def main():
    """Main entrypoint."""
    import argparse
    
    parser = argparse.ArgumentParser(description="L9 Mac Agent")
    parser.add_argument("--vps-url", default="http://localhost:8000", help="VPS API URL")
    parser.add_argument("--token", default="", help="Authentication token")
    parser.add_argument("--poll-interval", type=int, default=5, help="Poll interval in seconds")
    
    args = parser.parse_args()
    
    agent = MacAgent(
        vps_url=args.vps_url,
        auth_token=args.token,
        poll_interval=args.poll_interval
    )
    
    try:
        agent.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        agent.shutdown()


if __name__ == "__main__":
    main()

