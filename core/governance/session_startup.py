"""
L9 Core Governance - Session Startup Protocol
==============================================

Executable session startup protocol.
Converts patterns from profiles/session-startup-protocol.md into
programmatic preflight checks and mandatory file loading.

Key capabilities:
- Runs preflight checks (symlinks, config, directories)
- Loads mandatory startup files
- Returns structured status (not just instructions)
- Tracks loaded components for debugging

Version: 1.0.0
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = structlog.get_logger(__name__)


@dataclass
class StartupFile:
    """
    A mandatory startup file.
    
    Attributes:
        path: Relative path from workspace root
        component_id: Unique identifier (e.g., "PRF-SSP-001")
        required: Whether missing file is a failure
        description: What this file provides
    """
    
    path: str
    component_id: str
    required: bool = True
    description: str = ""


@dataclass
class PreflightResult:
    """Result of a preflight check."""
    
    name: str
    passed: bool
    message: str
    details: Optional[dict[str, Any]] = None


@dataclass
class StartupResult:
    """Complete startup protocol result."""
    
    status: str  # "READY", "DEGRADED", "BLOCKED"
    preflight_passed: bool
    files_loaded: list[str]
    files_failed: list[str]
    errors: list[str]
    warnings: list[str]
    started_at: datetime = field(default_factory=datetime.utcnow)
    duration_ms: int = 0


class SessionStartup:
    """
    Executable session startup protocol.
    
    Runs preflight checks and loads mandatory files,
    returning structured status for governance verification.
    
    Usage:
        startup = SessionStartup(Path("/Users/ib-mac/Projects/L9"))
        result = startup.execute()
        if result.status != "READY":
            # Handle startup issues
            pass
    """
    
    def __init__(self, workspace_root: Path) -> None:
        """
        Initialize startup protocol.
        
        Args:
            workspace_root: Path to workspace root directory
        """
        self.root = workspace_root
        self._files_loaded: list[str] = []
        self._errors: list[str] = []
        self._warnings: list[str] = []
    
    @property
    def mandatory_files(self) -> list[StartupFile]:
        """Get list of mandatory startup files."""
        return [
            # Core governance
            StartupFile(
                ".cursor-commands/profiles/session-startup-protocol.md",
                "PRF-SSP-001",
                required=True,
                description="Session startup protocol",
            ),
            StartupFile(
                ".cursor-commands/startup/REASONING_STACK.yaml",
                "REASONING-STACK-001",
                required=True,
                description="Reasoning activation config",
            ),
            # Learning files
            StartupFile(
                ".cursor-commands/learning/credentials-policy.md",
                "LRN-006",
                required=False,
                description="Credentials handling policy",
            ),
            StartupFile(
                ".cursor-commands/learning/failures/repeated-mistakes.md",
                "LRN-001",
                required=True,
                description="Critical mistake patterns",
            ),
            StartupFile(
                ".cursor-commands/learning/patterns/quick-fixes.md",
                "LRN-002",
                required=True,
                description="Quick fix patterns",
            ),
            # Startup files
            StartupFile(
                ".cursor-commands/startup/system_capabilities.md",
                "STARTUP-001",
                required=False,
                description="System capabilities manifest",
            ),
            StartupFile(
                ".cursor-commands/startup/probabilistic_governance_activated.md",
                "STARTUP-002",
                required=False,
                description="Probabilistic governance config",
            ),
            # Reasoning profiles
            StartupFile(
                ".cursor-commands/profiles/reasoning_docs.md",
                "PROFILE-001",
                required=False,
                description="Documentation reasoning mode",
            ),
            StartupFile(
                ".cursor-commands/profiles/reasoning_technical_operations.md",
                "PROFILE-002",
                required=False,
                description="Technical operations reasoning",
            ),
            # Operating modes
            StartupFile(
                ".cursor-commands/profiles/ynp_mode.md",
                "MODE-001",
                required=False,
                description="YNP co-pilot mode",
            ),
            StartupFile(
                ".cursor-commands/profiles/dev_mode.md",
                "MODE-002",
                required=False,
                description="Development automation mode",
            ),
            StartupFile(
                ".cursor-commands/profiles/orchestrator.md",
                "MODE-003",
                required=False,
                description="Orchestrator coordination mode",
            ),
            # Workflow state
            StartupFile(
                "workflow_state.md",
                "STATE-001",
                required=True,
                description="Workflow state tracking",
            ),
        ]
    
    def run_preflight(self) -> list[PreflightResult]:
        """
        Execute preflight checks.
        
        Returns:
            List of PreflightResult objects
        """
        results: list[PreflightResult] = []
        
        # Check 1: Workspace root exists
        results.append(PreflightResult(
            name="workspace_exists",
            passed=self.root.exists(),
            message=f"Workspace root: {self.root}",
        ))
        
        # Check 2: .cursor-commands symlink
        symlink = self.root / ".cursor-commands"
        symlink_valid = symlink.is_symlink() and symlink.exists()
        symlink_target = ""
        if symlink.is_symlink():
            try:
                symlink_target = str(symlink.resolve())
            except Exception:
                symlink_target = "unresolvable"
        
        results.append(PreflightResult(
            name="symlink_valid",
            passed=symlink_valid,
            message=f"Symlink target: {symlink_target}",
            details={"target": symlink_target, "is_symlink": symlink.is_symlink()},
        ))
        
        # Check 3: Symlink points to Dropbox (not Library)
        dropbox_valid = "Dropbox" in symlink_target
        results.append(PreflightResult(
            name="symlink_dropbox",
            passed=dropbox_valid,
            message="Symlink must point to Dropbox, not Library",
            details={"contains_dropbox": dropbox_valid},
        ))
        
        # Check 4: workflow_state.md exists
        workflow_state = self.root / "workflow_state.md"
        results.append(PreflightResult(
            name="workflow_state_exists",
            passed=workflow_state.exists(),
            message=f"Workflow state: {workflow_state}",
        ))
        
        # Check 5: core/governance/ exists
        gov_dir = self.root / "core" / "governance"
        results.append(PreflightResult(
            name="governance_dir_exists",
            passed=gov_dir.exists(),
            message=f"Governance directory: {gov_dir}",
        ))
        
        return results
    
    def load_mandatory_files(self) -> dict[str, Any]:
        """
        Load all mandatory startup files.
        
        Returns:
            Dict with loaded, failed, and total counts
        """
        results: dict[str, Any] = {
            "loaded": [],
            "failed": [],
            "total": len(self.mandatory_files),
        }
        
        for sf in self.mandatory_files:
            path = self.root / sf.path
            
            if path.exists():
                try:
                    # Just verify we can read it
                    content = path.read_text(encoding="utf-8")
                    self._files_loaded.append(sf.component_id)
                    results["loaded"].append({
                        "path": sf.path,
                        "component_id": sf.component_id,
                        "size_bytes": len(content),
                    })
                    logger.debug(
                        "session_startup.file_loaded",
                        path=sf.path,
                        component_id=sf.component_id,
                    )
                except Exception as e:
                    results["failed"].append({
                        "path": sf.path,
                        "error": str(e),
                    })
                    if sf.required:
                        self._errors.append(f"CRITICAL: Cannot read {sf.path}: {e}")
                    else:
                        self._warnings.append(f"Cannot read {sf.path}: {e}")
            else:
                results["failed"].append({
                    "path": sf.path,
                    "error": "File not found",
                })
                if sf.required:
                    self._errors.append(f"CRITICAL: Missing required file {sf.path}")
                else:
                    self._warnings.append(f"Optional file missing: {sf.path}")
        
        results["success"] = len([f for f in results["failed"] if "CRITICAL" in str(f)]) == 0
        return results
    
    def execute(self) -> StartupResult:
        """
        Execute full startup protocol.
        
        Returns:
            StartupResult with complete status
        """
        start_time = datetime.utcnow()
        
        # Clear state
        self._files_loaded = []
        self._errors = []
        self._warnings = []
        
        # Run preflight
        preflight_results = self.run_preflight()
        preflight_passed = all(r.passed for r in preflight_results if r.name in [
            "workspace_exists", "workflow_state_exists"
        ])
        
        if not preflight_passed:
            for r in preflight_results:
                if not r.passed:
                    self._errors.append(f"Preflight failed: {r.name} - {r.message}")
            
            return StartupResult(
                status="BLOCKED",
                preflight_passed=False,
                files_loaded=[],
                files_failed=[r.name for r in preflight_results if not r.passed],
                errors=self._errors,
                warnings=self._warnings,
                duration_ms=self._calc_duration_ms(start_time),
            )
        
        # Load mandatory files
        file_results = self.load_mandatory_files()
        
        # Determine status
        critical_failures = [e for e in self._errors if "CRITICAL" in e]
        if critical_failures:
            status = "BLOCKED"
        elif self._warnings:
            status = "DEGRADED"
        else:
            status = "READY"
        
        duration_ms = self._calc_duration_ms(start_time)
        
        logger.info(
            "session_startup.complete",
            status=status,
            files_loaded=len(file_results["loaded"]),
            files_failed=len(file_results["failed"]),
            duration_ms=duration_ms,
        )
        
        return StartupResult(
            status=status,
            preflight_passed=preflight_passed,
            files_loaded=self._files_loaded,
            files_failed=[f["path"] for f in file_results["failed"]],
            errors=self._errors,
            warnings=self._warnings,
            duration_ms=duration_ms,
        )
    
    def _calc_duration_ms(self, start_time: datetime) -> int:
        """Calculate duration in milliseconds."""
        return int((datetime.utcnow() - start_time).total_seconds() * 1000)


# Factory function
def create_session_startup(workspace_root: Optional[Path] = None) -> SessionStartup:
    """
    Create a SessionStartup instance.
    
    Args:
        workspace_root: Workspace root (defaults to L9 project)
        
    Returns:
        Configured SessionStartup
    """
    root = workspace_root or Path("/Users/ib-mac/Projects/L9")
    return SessionStartup(root)


__all__ = [
    "SessionStartup",
    "StartupFile",
    "PreflightResult",
    "StartupResult",
    "create_session_startup",
]

