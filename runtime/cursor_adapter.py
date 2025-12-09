"""
L9 Runtime - Cursor IDE Adapter
===============================
Version: 2.0.0

Integration with Cursor IDE for deterministic, resumable execution.

Features:
- Patch files in-editor
- Resolve conflicts
- Update code via Cursor APIs
- Editor state management
- Command execution
- PacketEnvelope emission

Compatibility:
- Memory substrate (PacketEnvelope v1.1.0)
- World model integration
- IR Engine integration
"""

from __future__ import annotations

import asyncio
import difflib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Callable, Union
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class CommandType(str, Enum):
    """Types of Cursor commands."""
    OPEN_FILE = "open_file"
    CLOSE_FILE = "close_file"
    EDIT_FILE = "edit_file"
    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    NAVIGATE = "navigate"
    SEARCH = "search"
    RUN_TERMINAL = "run_terminal"
    SHOW_MESSAGE = "show_message"
    REQUEST_INPUT = "request_input"
    APPLY_PATCH = "apply_patch"
    RESOLVE_CONFLICT = "resolve_conflict"
    SAVE_FILE = "save_file"
    SAVE_ALL = "save_all"
    REFRESH = "refresh"


class PatchType(str, Enum):
    """Types of file patches."""
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"
    APPEND = "append"
    PREPEND = "prepend"


class ConflictResolution(str, Enum):
    """How to resolve conflicts."""
    OURS = "ours"  # Keep our changes
    THEIRS = "theirs"  # Accept their changes
    MERGE = "merge"  # Attempt to merge
    MANUAL = "manual"  # Require manual resolution
    ABORT = "abort"  # Abort operation


class CommandStatus(str, Enum):
    """Status of a command."""
    PENDING = "pending"
    SENT = "sent"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class TextEdit:
    """A single text edit operation."""
    edit_id: UUID = field(default_factory=uuid4)
    edit_type: PatchType = PatchType.REPLACE
    start_line: int = 1
    start_column: int = 1
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    old_text: str = ""
    new_text: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "edit_id": str(self.edit_id),
            "edit_type": self.edit_type.value,
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "old_text": self.old_text,
            "new_text": self.new_text,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TextEdit:
        """Deserialize from dictionary."""
        return cls(
            edit_id=UUID(data["edit_id"]) if data.get("edit_id") else uuid4(),
            edit_type=PatchType(data.get("edit_type", "replace")),
            start_line=data.get("start_line", 1),
            start_column=data.get("start_column", 1),
            end_line=data.get("end_line"),
            end_column=data.get("end_column"),
            old_text=data.get("old_text", ""),
            new_text=data.get("new_text", ""),
        )


@dataclass
class FilePatch:
    """A collection of edits to apply to a file."""
    patch_id: UUID = field(default_factory=uuid4)
    path: str = ""
    edits: list[TextEdit] = field(default_factory=list)
    description: str = ""
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    applied_at: Optional[datetime] = None
    reverted_at: Optional[datetime] = None
    
    # Original content for rollback
    original_content: Optional[str] = None
    
    # Result
    success: bool = False
    error: Optional[str] = None
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "patch_id": str(self.patch_id),
            "path": self.path,
            "edits": [e.to_dict() for e in self.edits],
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "reverted_at": self.reverted_at.isoformat() if self.reverted_at else None,
            "success": self.success,
            "error": self.error,
            "conflicts": self.conflicts,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FilePatch:
        """Deserialize from dictionary."""
        return cls(
            patch_id=UUID(data["patch_id"]) if data.get("patch_id") else uuid4(),
            path=data.get("path", ""),
            edits=[TextEdit.from_dict(e) for e in data.get("edits", [])],
            description=data.get("description", ""),
            author=data.get("author"),
            original_content=data.get("original_content"),
            success=data.get("success", False),
            error=data.get("error"),
            conflicts=data.get("conflicts", []),
        )


@dataclass
class ConflictInfo:
    """Information about a conflict."""
    conflict_id: UUID = field(default_factory=uuid4)
    path: str = ""
    start_line: int = 0
    end_line: int = 0
    our_content: str = ""
    their_content: str = ""
    base_content: str = ""
    resolution: Optional[ConflictResolution] = None
    resolved_content: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "conflict_id": str(self.conflict_id),
            "path": self.path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "our_content": self.our_content,
            "their_content": self.their_content,
            "base_content": self.base_content,
            "resolution": self.resolution.value if self.resolution else None,
            "resolved_content": self.resolved_content,
        }


@dataclass
class CursorCommand:
    """A command for Cursor IDE."""
    command_id: UUID = field(default_factory=uuid4)
    command_type: CommandType = CommandType.SHOW_MESSAGE
    parameters: dict[str, Any] = field(default_factory=dict)
    status: CommandStatus = CommandStatus.PENDING
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_ms: int = 30000
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "command_id": str(self.command_id),
            "command_type": self.command_type.value,
            "parameters": self.parameters,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class EditorState:
    """Current state of the editor."""
    open_files: list[str] = field(default_factory=list)
    active_file: Optional[str] = None
    cursor_position: Optional[tuple[int, int]] = None  # (line, column)
    selection: Optional[tuple[tuple[int, int], tuple[int, int]]] = None  # ((start_line, start_col), (end_line, end_col))
    workspace_path: Optional[str] = None
    modified_files: list[str] = field(default_factory=list)
    visible_range: Optional[tuple[int, int]] = None  # (start_line, end_line)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "open_files": self.open_files,
            "active_file": self.active_file,
            "cursor_position": self.cursor_position,
            "selection": self.selection,
            "workspace_path": self.workspace_path,
            "modified_files": self.modified_files,
            "visible_range": self.visible_range,
        }


@dataclass
class AdapterConfig:
    """Configuration for Cursor adapter."""
    workspace_path: Optional[str] = None
    command_timeout_ms: int = 30000
    max_retries: int = 3
    auto_save: bool = True
    backup_before_patch: bool = True
    emit_packets: bool = True
    conflict_resolution_default: ConflictResolution = ConflictResolution.MANUAL


# =============================================================================
# Cursor Adapter
# =============================================================================

class CursorAdapter:
    """
    Adapter for Cursor IDE integration with patch and conflict resolution.
    
    Features:
    - Patch files in-editor
    - Resolve conflicts
    - Update code via Cursor APIs
    - Editor state management
    - Command execution
    - PacketEnvelope emission
    
    Note: In production, this interfaces with Cursor's extension API.
    This implementation provides the interface and simulation.
    """
    
    def __init__(self, config: Optional[AdapterConfig] = None):
        """
        Initialize the Cursor adapter.
        
        Args:
            config: Adapter configuration
        """
        self._config = config or AdapterConfig()
        self._state = EditorState(workspace_path=self._config.workspace_path)
        self._command_history: list[CursorCommand] = []
        self._patch_history: list[FilePatch] = []
        self._pending_conflicts: dict[UUID, ConflictInfo] = {}
        self._connected = False
        self._packet_emitter: Optional[Callable] = None
        self._command_handlers: dict[CommandType, Callable] = {}
        self._lock = asyncio.Lock()
        
        # Register default handlers
        self._register_default_handlers()
        
        logger.info(f"CursorAdapter initialized (workspace={self._config.workspace_path})")
    
    def set_packet_emitter(self, emitter: Callable) -> None:
        """Set the packet emitter function."""
        self._packet_emitter = emitter
    
    def _register_default_handlers(self) -> None:
        """Register default command handlers."""
        self._command_handlers = {
            CommandType.OPEN_FILE: self._handle_open_file,
            CommandType.CLOSE_FILE: self._handle_close_file,
            CommandType.EDIT_FILE: self._handle_edit_file,
            CommandType.CREATE_FILE: self._handle_create_file,
            CommandType.DELETE_FILE: self._handle_delete_file,
            CommandType.NAVIGATE: self._handle_navigate,
            CommandType.SEARCH: self._handle_search,
            CommandType.APPLY_PATCH: self._handle_apply_patch,
            CommandType.RESOLVE_CONFLICT: self._handle_resolve_conflict,
            CommandType.SAVE_FILE: self._handle_save_file,
            CommandType.SAVE_ALL: self._handle_save_all,
        }
    
    # ==========================================================================
    # Connection
    # ==========================================================================
    
    async def connect(self) -> bool:
        """
        Connect to Cursor IDE.
        
        Returns:
            True if connected
        """
        async with self._lock:
            # In production: establish connection to Cursor extension
            self._connected = True
            logger.info("Connected to Cursor IDE")
            
            await self._emit_event("cursor_connected", {
                "workspace": self._config.workspace_path,
            })
            
            return True
    
    async def disconnect(self) -> None:
        """Disconnect from Cursor IDE."""
        async with self._lock:
            self._connected = False
            
            await self._emit_event("cursor_disconnected", {})
            
            logger.info("Disconnected from Cursor IDE")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
    
    # ==========================================================================
    # Patch Operations
    # ==========================================================================
    
    async def apply_patch(
        self,
        path: str,
        edits: list[Union[TextEdit, dict[str, Any]]],
        description: str = "",
        author: Optional[str] = None,
        dry_run: bool = False,
    ) -> FilePatch:
        """
        Apply a patch to a file.
        
        Args:
            path: File path
            edits: List of text edits
            description: Patch description
            author: Author of the patch
            dry_run: If True, don't actually apply
            
        Returns:
            FilePatch with result
        """
        # Convert dict edits to TextEdit objects
        text_edits = []
        for edit in edits:
            if isinstance(edit, dict):
                text_edits.append(TextEdit.from_dict(edit))
            else:
                text_edits.append(edit)
        
        patch = FilePatch(
            path=path,
            edits=text_edits,
            description=description,
            author=author,
        )
        
        try:
            # Read current content
            full_path = self._resolve_path(path)
            
            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as f:
                    original_content = f.read()
                patch.original_content = original_content
            else:
                original_content = ""
            
            # Apply edits to content
            new_content = await self._apply_edits_to_content(original_content, text_edits)
            
            # Check for conflicts
            conflicts = await self._detect_conflicts(path, original_content, new_content)
            
            if conflicts:
                patch.conflicts = [c.to_dict() for c in conflicts]
                
                if not dry_run:
                    # Store conflicts for resolution
                    for conflict in conflicts:
                        self._pending_conflicts[conflict.conflict_id] = conflict
                    
                    patch.error = f"Found {len(conflicts)} conflicts"
                    return patch
            
            if dry_run:
                patch.success = True
                return patch
            
            # Write new content
            if self._config.backup_before_patch:
                backup_path = full_path.with_suffix(full_path.suffix + ".backup")
                if full_path.exists():
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(original_content)
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            patch.success = True
            patch.applied_at = datetime.utcnow()
            
            # Update editor state
            if path not in self._state.modified_files:
                self._state.modified_files.append(path)
            
            # Emit packet
            await self._emit_event("patch_applied", {
                "patch_id": str(patch.patch_id),
                "path": path,
                "edit_count": len(text_edits),
            })
            
            logger.info(f"Applied patch to {path} ({len(text_edits)} edits)")
            
        except Exception as e:
            patch.error = str(e)
            logger.error(f"Failed to apply patch to {path}: {e}")
        
        self._patch_history.append(patch)
        return patch
    
    async def revert_patch(self, patch_id: UUID) -> bool:
        """
        Revert a previously applied patch.
        
        Args:
            patch_id: Patch ID
            
        Returns:
            True if reverted
        """
        # Find patch
        patch = None
        for p in self._patch_history:
            if p.patch_id == patch_id:
                patch = p
                break
        
        if not patch:
            logger.warning(f"Patch not found: {patch_id}")
            return False
        
        if not patch.original_content:
            logger.warning(f"No original content for patch: {patch_id}")
            return False
        
        try:
            full_path = self._resolve_path(patch.path)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(patch.original_content)
            
            patch.reverted_at = datetime.utcnow()
            
            await self._emit_event("patch_reverted", {
                "patch_id": str(patch_id),
                "path": patch.path,
            })
            
            logger.info(f"Reverted patch {patch_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revert patch: {e}")
            return False
    
    async def _apply_edits_to_content(
        self,
        content: str,
        edits: list[TextEdit],
    ) -> str:
        """Apply edits to content string."""
        lines = content.splitlines(keepends=True)
        if not lines:
            lines = [""]
        
        # Sort edits by position (reverse order to apply from bottom to top)
        sorted_edits = sorted(
            edits,
            key=lambda e: (e.start_line, e.start_column),
            reverse=True,
        )
        
        for edit in sorted_edits:
            if edit.edit_type == PatchType.INSERT:
                # Insert at position
                if edit.start_line <= len(lines):
                    line_idx = edit.start_line - 1
                    line = lines[line_idx] if line_idx < len(lines) else ""
                    col = edit.start_column - 1
                    
                    new_line = line[:col] + edit.new_text + line[col:]
                    lines[line_idx] = new_line
                else:
                    lines.append(edit.new_text)
            
            elif edit.edit_type == PatchType.DELETE:
                # Delete range
                if edit.end_line and edit.end_column:
                    start_idx = edit.start_line - 1
                    end_idx = edit.end_line - 1
                    
                    if start_idx == end_idx:
                        # Single line delete
                        line = lines[start_idx]
                        lines[start_idx] = line[:edit.start_column - 1] + line[edit.end_column - 1:]
                    else:
                        # Multi-line delete
                        start_line = lines[start_idx][:edit.start_column - 1]
                        end_line = lines[end_idx][edit.end_column - 1:] if end_idx < len(lines) else ""
                        
                        lines[start_idx] = start_line + end_line
                        del lines[start_idx + 1:end_idx + 1]
            
            elif edit.edit_type == PatchType.REPLACE:
                # Replace range or search/replace
                if edit.old_text:
                    # Search and replace
                    full_content = "".join(lines)
                    full_content = full_content.replace(edit.old_text, edit.new_text, 1)
                    lines = full_content.splitlines(keepends=True)
                    if not lines:
                        lines = [""]
                elif edit.end_line and edit.end_column:
                    # Range replace
                    start_idx = edit.start_line - 1
                    end_idx = edit.end_line - 1
                    
                    if start_idx == end_idx:
                        line = lines[start_idx]
                        lines[start_idx] = (
                            line[:edit.start_column - 1] +
                            edit.new_text +
                            line[edit.end_column - 1:]
                        )
                    else:
                        start_line = lines[start_idx][:edit.start_column - 1]
                        end_line = lines[end_idx][edit.end_column - 1:] if end_idx < len(lines) else ""
                        
                        lines[start_idx] = start_line + edit.new_text + end_line
                        del lines[start_idx + 1:end_idx + 1]
            
            elif edit.edit_type == PatchType.APPEND:
                # Append to end
                if lines and lines[-1].endswith("\n"):
                    lines.append(edit.new_text)
                else:
                    lines.append("\n" + edit.new_text)
            
            elif edit.edit_type == PatchType.PREPEND:
                # Prepend to beginning
                lines.insert(0, edit.new_text + "\n")
        
        return "".join(lines)
    
    # ==========================================================================
    # Conflict Resolution
    # ==========================================================================
    
    async def _detect_conflicts(
        self,
        path: str,
        original: str,
        modified: str,
    ) -> list[ConflictInfo]:
        """
        Detect conflicts between original and modified content.
        
        In a real implementation, this would check against the file system
        or version control to detect if the file changed since reading.
        """
        # For now, return empty (no conflicts in simulation)
        return []
    
    async def resolve_conflict(
        self,
        conflict_id: UUID,
        resolution: ConflictResolution,
        resolved_content: Optional[str] = None,
    ) -> bool:
        """
        Resolve a conflict.
        
        Args:
            conflict_id: Conflict ID
            resolution: Resolution strategy
            resolved_content: Content if resolution is MANUAL
            
        Returns:
            True if resolved
        """
        conflict = self._pending_conflicts.get(conflict_id)
        if not conflict:
            logger.warning(f"Conflict not found: {conflict_id}")
            return False
        
        try:
            final_content = None
            
            if resolution == ConflictResolution.OURS:
                final_content = conflict.our_content
            elif resolution == ConflictResolution.THEIRS:
                final_content = conflict.their_content
            elif resolution == ConflictResolution.MERGE:
                # Attempt automatic merge
                final_content = self._attempt_merge(
                    conflict.base_content,
                    conflict.our_content,
                    conflict.their_content,
                )
                if final_content is None:
                    logger.warning("Automatic merge failed")
                    return False
            elif resolution == ConflictResolution.MANUAL:
                if resolved_content is None:
                    logger.warning("Manual resolution requires resolved_content")
                    return False
                final_content = resolved_content
            elif resolution == ConflictResolution.ABORT:
                del self._pending_conflicts[conflict_id]
                return True
            
            conflict.resolution = resolution
            conflict.resolved_content = final_content
            
            # Apply resolution to file
            full_path = self._resolve_path(conflict.path)
            if final_content:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                lines = content.splitlines(keepends=True)
                
                # Replace conflict region
                new_lines = (
                    lines[:conflict.start_line - 1] +
                    [final_content] +
                    lines[conflict.end_line:]
                )
                
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("".join(new_lines))
            
            del self._pending_conflicts[conflict_id]
            
            await self._emit_event("conflict_resolved", {
                "conflict_id": str(conflict_id),
                "path": conflict.path,
                "resolution": resolution.value,
            })
            
            logger.info(f"Resolved conflict {conflict_id} with {resolution.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve conflict: {e}")
            return False
    
    def _attempt_merge(
        self,
        base: str,
        ours: str,
        theirs: str,
    ) -> Optional[str]:
        """Attempt to automatically merge three versions."""
        # Simple three-way merge using difflib
        try:
            base_lines = base.splitlines(keepends=True)
            ours_lines = ours.splitlines(keepends=True)
            theirs_lines = theirs.splitlines(keepends=True)
            
            # Get diffs
            ours_diff = list(difflib.unified_diff(base_lines, ours_lines))
            theirs_diff = list(difflib.unified_diff(base_lines, theirs_lines))
            
            # If no overlapping changes, merge is possible
            # This is a simplified check
            if not ours_diff or not theirs_diff:
                return ours if not theirs_diff else theirs
            
            # For now, return None to indicate manual resolution needed
            return None
            
        except Exception:
            return None
    
    def get_pending_conflicts(self) -> list[ConflictInfo]:
        """Get list of pending conflicts."""
        return list(self._pending_conflicts.values())
    
    # ==========================================================================
    # File Operations
    # ==========================================================================
    
    async def open_file(self, path: str) -> CursorCommand:
        """
        Open a file in the editor.
        
        Args:
            path: File path
            
        Returns:
            CursorCommand
        """
        command = CursorCommand(
            command_type=CommandType.OPEN_FILE,
            parameters={"path": path},
        )
        
        result = await self._execute_command(command)
        
        if result.status == CommandStatus.COMPLETED:
            if path not in self._state.open_files:
                self._state.open_files.append(path)
            self._state.active_file = path
        
        return result
    
    async def close_file(self, path: str) -> CursorCommand:
        """
        Close a file.
        
        Args:
            path: File path
            
        Returns:
            CursorCommand
        """
        command = CursorCommand(
            command_type=CommandType.CLOSE_FILE,
            parameters={"path": path},
        )
        
        result = await self._execute_command(command)
        
        if result.status == CommandStatus.COMPLETED:
            if path in self._state.open_files:
                self._state.open_files.remove(path)
            if self._state.active_file == path:
                self._state.active_file = (
                    self._state.open_files[0]
                    if self._state.open_files
                    else None
                )
        
        return result
    
    async def create_file(
        self,
        path: str,
        content: str = "",
    ) -> CursorCommand:
        """
        Create a new file.
        
        Args:
            path: File path
            content: Initial content
            
        Returns:
            CursorCommand
        """
        command = CursorCommand(
            command_type=CommandType.CREATE_FILE,
            parameters={"path": path, "content": content},
        )
        
        return await self._execute_command(command)
    
    async def edit_file(
        self,
        path: str,
        edits: list[dict[str, Any]],
    ) -> CursorCommand:
        """
        Apply edits to a file.
        
        Args:
            path: File path
            edits: List of edit operations
            
        Returns:
            CursorCommand
        """
        command = CursorCommand(
            command_type=CommandType.EDIT_FILE,
            parameters={"path": path, "edits": edits},
        )
        
        return await self._execute_command(command)
    
    async def delete_file(self, path: str) -> CursorCommand:
        """
        Delete a file.
        
        Args:
            path: File path
            
        Returns:
            CursorCommand
        """
        command = CursorCommand(
            command_type=CommandType.DELETE_FILE,
            parameters={"path": path},
        )
        
        result = await self._execute_command(command)
        
        if result.status == CommandStatus.COMPLETED and path in self._state.open_files:
            self._state.open_files.remove(path)
        
        return result
    
    async def save_file(self, path: Optional[str] = None) -> CursorCommand:
        """
        Save a file.
        
        Args:
            path: File path (or active file if None)
            
        Returns:
            CursorCommand
        """
        target_path = path or self._state.active_file
        
        command = CursorCommand(
            command_type=CommandType.SAVE_FILE,
            parameters={"path": target_path},
        )
        
        result = await self._execute_command(command)
        
        if result.status == CommandStatus.COMPLETED and target_path:
            if target_path in self._state.modified_files:
                self._state.modified_files.remove(target_path)
        
        return result
    
    async def save_all(self) -> CursorCommand:
        """
        Save all modified files.
        
        Returns:
            CursorCommand
        """
        command = CursorCommand(
            command_type=CommandType.SAVE_ALL,
            parameters={},
        )
        
        result = await self._execute_command(command)
        
        if result.status == CommandStatus.COMPLETED:
            self._state.modified_files.clear()
        
        return result
    
    # ==========================================================================
    # Navigation
    # ==========================================================================
    
    async def navigate_to(
        self,
        path: str,
        line: int = 1,
        column: int = 1,
    ) -> CursorCommand:
        """
        Navigate to a location.
        
        Args:
            path: File path
            line: Line number
            column: Column number
            
        Returns:
            CursorCommand
        """
        command = CursorCommand(
            command_type=CommandType.NAVIGATE,
            parameters={"path": path, "line": line, "column": column},
        )
        
        result = await self._execute_command(command)
        
        if result.status == CommandStatus.COMPLETED:
            self._state.active_file = path
            self._state.cursor_position = (line, column)
        
        return result
    
    async def search(
        self,
        query: str,
        path: Optional[str] = None,
        regex: bool = False,
    ) -> CursorCommand:
        """
        Search in files.
        
        Args:
            query: Search query
            path: Optional path to search in
            regex: Whether query is regex
            
        Returns:
            CursorCommand with results
        """
        command = CursorCommand(
            command_type=CommandType.SEARCH,
            parameters={"query": query, "path": path, "regex": regex},
        )
        
        return await self._execute_command(command)
    
    # ==========================================================================
    # Terminal
    # ==========================================================================
    
    async def run_terminal_command(
        self,
        command_text: str,
        wait: bool = True,
    ) -> CursorCommand:
        """
        Run a terminal command.
        
        Args:
            command_text: Command to run
            wait: Whether to wait for completion
            
        Returns:
            CursorCommand
        """
        command = CursorCommand(
            command_type=CommandType.RUN_TERMINAL,
            parameters={"command": command_text, "wait": wait},
        )
        
        return await self._execute_command(command)
    
    # ==========================================================================
    # Messages
    # ==========================================================================
    
    async def show_message(
        self,
        message: str,
        message_type: str = "info",
    ) -> CursorCommand:
        """
        Show a message in the IDE.
        
        Args:
            message: Message text
            message_type: Type (info, warning, error)
            
        Returns:
            CursorCommand
        """
        command = CursorCommand(
            command_type=CommandType.SHOW_MESSAGE,
            parameters={"message": message, "type": message_type},
        )
        
        return await self._execute_command(command)
    
    async def request_input(
        self,
        prompt: str,
        default: str = "",
    ) -> CursorCommand:
        """
        Request input from user.
        
        Args:
            prompt: Input prompt
            default: Default value
            
        Returns:
            CursorCommand with user input in result
        """
        command = CursorCommand(
            command_type=CommandType.REQUEST_INPUT,
            parameters={"prompt": prompt, "default": default},
        )
        
        return await self._execute_command(command)
    
    # ==========================================================================
    # Command Execution
    # ==========================================================================
    
    async def _execute_command(self, command: CursorCommand) -> CursorCommand:
        """Execute a command."""
        async with self._lock:
            command.status = CommandStatus.SENT
            command.sent_at = datetime.utcnow()
            
            try:
                # Get handler
                handler = self._command_handlers.get(command.command_type)
                
                if handler:
                    command.status = CommandStatus.EXECUTING
                    result = await handler(command.parameters)
                    command.result = result
                    command.status = CommandStatus.COMPLETED
                else:
                    # Default simulation for unhandled commands
                    command.status = CommandStatus.COMPLETED
                    command.result = {
                        "success": True,
                        "command_type": command.command_type.value,
                    }
                
            except asyncio.TimeoutError:
                command.status = CommandStatus.FAILED
                command.error = "Command timeout"
            except Exception as e:
                command.status = CommandStatus.FAILED
                command.error = str(e)
            
            command.completed_at = datetime.utcnow()
            self._command_history.append(command)
            
            # Emit event
            await self._emit_event("command_executed", {
                "command_id": str(command.command_id),
                "command_type": command.command_type.value,
                "status": command.status.value,
            })
            
            logger.debug(f"Executed command: {command.command_type.value}")
            
            return command
    
    # ==========================================================================
    # Command Handlers
    # ==========================================================================
    
    async def _handle_open_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle open file command."""
        path = params.get("path", "")
        full_path = self._resolve_path(path)
        
        return {
            "success": full_path.exists(),
            "path": path,
        }
    
    async def _handle_close_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle close file command."""
        return {"success": True, "path": params.get("path", "")}
    
    async def _handle_edit_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle edit file command."""
        path = params.get("path", "")
        edits = params.get("edits", [])
        
        # Apply via patch
        patch = await self.apply_patch(path, edits)
        
        return {
            "success": patch.success,
            "patch_id": str(patch.patch_id),
            "error": patch.error,
        }
    
    async def _handle_create_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle create file command."""
        path = params.get("path", "")
        content = params.get("content", "")
        
        full_path = self._resolve_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return {"success": True, "path": path}
    
    async def _handle_delete_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle delete file command."""
        path = params.get("path", "")
        full_path = self._resolve_path(path)
        
        if full_path.exists():
            full_path.unlink()
            return {"success": True, "path": path}
        
        return {"success": False, "error": "File not found"}
    
    async def _handle_navigate(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle navigate command."""
        return {
            "success": True,
            "path": params.get("path", ""),
            "line": params.get("line", 1),
            "column": params.get("column", 1),
        }
    
    async def _handle_search(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle search command."""
        # In production, this would use Cursor's search API
        return {
            "success": True,
            "query": params.get("query", ""),
            "results": [],
        }
    
    async def _handle_apply_patch(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle apply patch command."""
        path = params.get("path", "")
        edits = params.get("edits", [])
        
        patch = await self.apply_patch(path, edits)
        
        return {
            "success": patch.success,
            "patch_id": str(patch.patch_id),
            "error": patch.error,
        }
    
    async def _handle_resolve_conflict(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle resolve conflict command."""
        conflict_id = UUID(params.get("conflict_id", ""))
        resolution = ConflictResolution(params.get("resolution", "manual"))
        resolved_content = params.get("resolved_content")
        
        success = await self.resolve_conflict(conflict_id, resolution, resolved_content)
        
        return {"success": success}
    
    async def _handle_save_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle save file command."""
        return {"success": True, "path": params.get("path", "")}
    
    async def _handle_save_all(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle save all command."""
        return {"success": True, "files_saved": len(self._state.modified_files)}
    
    # ==========================================================================
    # Event Emission
    # ==========================================================================
    
    async def _emit_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Emit an event packet."""
        if not self._config.emit_packets or not self._packet_emitter:
            return
        
        try:
            await self._packet_emitter({
                "packet_id": str(uuid4()),
                "packet_type": "cursor_event",
                "payload": {
                    "kind": "cursor_event",
                    "event_type": event_type,
                    **payload,
                },
                "metadata": {
                    "domain": "cursor_adapter",
                },
                "tags": ["cursor", event_type],
            })
        except Exception as e:
            logger.error(f"Failed to emit event: {e}")
    
    # ==========================================================================
    # State
    # ==========================================================================
    
    def get_state(self) -> EditorState:
        """Get current editor state."""
        return self._state
    
    def get_open_files(self) -> list[str]:
        """Get list of open files."""
        return self._state.open_files.copy()
    
    def get_active_file(self) -> Optional[str]:
        """Get active file path."""
        return self._state.active_file
    
    def get_modified_files(self) -> list[str]:
        """Get list of modified files."""
        return self._state.modified_files.copy()
    
    def get_command_history(self, limit: int = 100) -> list[CursorCommand]:
        """Get command history."""
        return self._command_history[-limit:]
    
    def get_patch_history(self, limit: int = 100) -> list[FilePatch]:
        """Get patch history."""
        return self._patch_history[-limit:]
    
    # ==========================================================================
    # Utility
    # ==========================================================================
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace."""
        if self._config.workspace_path:
            return Path(self._config.workspace_path) / path
        return Path(path)
