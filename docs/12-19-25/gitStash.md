admin@L9:/opt/l9$ git stash show -p | head -100
diff --git a/api/db.py b/api/db.py
index ae836d6..43e0e79 100644
--- a/api/db.py
+++ b/api/db.py
@@ -1,7 +1,8 @@
+import os
 import psycopg
 from psycopg.rows import dict_row
 
-MEMORY_DSN = "postgresql://postgres:8e4fXWM6Q3M87*b3@127.0.0.1:5432/l9_memory"
+MEMORY_DSN = os.environ.get("MEMORY_DSN", "postgresql://postgres:postgres@127.0.0.1:5432/l9_memory")
 
 def init_db():
     with psycopg.connect(MEMORY_DSN, autocommit=True) as conn:
diff --git a/api/webhook_mac_agent.py b/api/webhook_mac_agent.py
index 1d7db65..8085ae4 100644
--- a/api/webhook_mac_agent.py
+++ b/api/webhook_mac_agent.py
@@ -1,129 +1,82 @@
 """
-Mac Agent API endpoints for polling and reporting task results.
+Mac Agent API Endpoints
+
+Polling-based task delivery for Mac Agent.
+Endpoints:
+- GET /mac/tasks/next - Mac agent polls for next task
+- POST /mac/tasks/{task_id}/result - Mac agent submits task result
 """
-import logging
-from fastapi import APIRouter, HTTPException
-from pydantic import BaseModel
-from typing import Optional, List
 
-from services.mac_tasks import get_next_task, complete_task, list_tasks
+from fastapi import APIRouter, HTTPException, Depends
+import logging
 
 logger = logging.getLogger(__name__)
 
 router = APIRouter(prefix="/mac", tags=["mac-agent"])
 
-class TaskResultRequest(BaseModel):
-    """Request model for task result submission."""
-    result: str
-    status: str = "done"
-    screenshot_path: Optional[str] = None
-    logs: Optional[List[str]] = None
 
 @router.get("/tasks/next")
 def get_next_mac_task():
     """
-    Get the next queued Mac task.
-    Returns null if no task is available.
-    """
-    task = get_next_task()
-    if task is None:
-        return {"task": None}
-    
-    task_dict = {
-        "id": task.id,
-        "source": task.source,
-        "channel": task.channel,
-        "user": task.user,
-    }
-    
-    # Include command (legacy) or steps (V2)
-    if task.command:
-        task_dict["command"] = task.command
-    if task.steps:
-        task_dict["steps"] = task.steps
+    Get the next queued task for Mac agent.
     
-    # Include file attachments if present
-    if task.attachments:
-        task_dict["attachments"] = task.attachments
-    
-    return {"task": task_dict}
+    Returns:
+        {
+            "task_id": "...",
+            "type": "automation",
+            "steps": [...],
+            "timeout": 300
+        }
+    or null if no tasks
+    """
+    try:
+        # TODO: Implement task queue lookup
+        # This should:
+        # 1. Query database for tasks where agent_type='mac' and status='pending'
+        # 2. Mark first task as 'assigned'
+        # 3. Return task data
+        logger.info("Mac agent polled for task")
+        return {"message": "No tasks available"}
+    except Exception as e:
+        logger.error(f"Error in get_next_mac_task: {e}", exc_info=True)
+        raise HTTPException(status_code=500, detail=str(e))
+
 
 @router.post("/tasks/{task_id}/result")