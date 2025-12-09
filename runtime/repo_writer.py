"""
L9 Runtime - Repository Writer
==============================
Version: 2.0.0

Safe write operations for deterministic, resumable execution.

Features:
- Safe write operations
- Dry-run mode
- Atomic apply (all-or-nothing)
- Rollback support
- Transaction management
- PacketEnvelope emission

Compatibility:
- Memory substrate (PacketEnvelope v1.1.0)
- World model integration
- IR Engine integration
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import shutil
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

class WriteOperationType(str, Enum):
    """Type of write operation."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RENAME = "rename"
    MOVE = "move"
    MKDIR = "mkdir"


class TransactionStatus(str, Enum):
    """Status of a transaction."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class WriteOperation:
    """A single write operation."""
    operation_id: UUID = field(default_factory=uuid4)
    operation_type: WriteOperationType = WriteOperationType.CREATE
    path: str = ""
    content: Optional[Union[str, bytes]] = None
    new_path: Optional[str] = None  # For rename/move
    encoding: str = "utf-8"
    is_binary: bool = False
    
    # State
    executed: bool = False
    success: bool = False
    error: Optional[str] = None
    
    # Backup for rollback
    backup_content: Optional[Union[str, bytes]] = None
    backup_existed: bool = False
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None
    bytes_written: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "operation_id": str(self.operation_id),
            "operation_type": self.operation_type.value,
            "path": self.path,
            "new_path": self.new_path,
            "encoding": self.encoding,
            "is_binary": self.is_binary,
            "executed": self.executed,
            "success": self.success,
            "error": self.error,
            "backup_existed": self.backup_existed,
            "timestamp": self.timestamp.isoformat(),
            "checksum": self.checksum,
            "bytes_written": self.bytes_written,
        }


@dataclass
class WriteResult:
    """Result of a write operation."""
    write_id: UUID = field(default_factory=uuid4)
    path: str = ""
    success: bool = False
    backup_path: Optional[str] = None
    bytes_written: int = 0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None
    operation_type: WriteOperationType = WriteOperationType.CREATE
    dry_run: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "write_id": str(self.write_id),
            "path": self.path,
            "success": self.success,
            "backup_path": self.backup_path,
            "bytes_written": self.bytes_written,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "checksum": self.checksum,
            "operation_type": self.operation_type.value,
            "dry_run": self.dry_run,
        }


@dataclass
class WriteTransaction:
    """A transaction containing multiple write operations."""
    transaction_id: UUID = field(default_factory=uuid4)
    status: TransactionStatus = TransactionStatus.PENDING
    operations: list[WriteOperation] = field(default_factory=list)
    results: list[WriteResult] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    committed_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    
    # Metadata
    description: str = ""
    agent_id: Optional[str] = None
    task_id: Optional[UUID] = None
    dry_run: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "transaction_id": str(self.transaction_id),
            "status": self.status.value,
            "operations": [op.to_dict() for op in self.operations],
            "results": [r.to_dict() for r in self.results],
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "committed_at": self.committed_at.isoformat() if self.committed_at else None,
            "rolled_back_at": self.rolled_back_at.isoformat() if self.rolled_back_at else None,
            "description": self.description,
            "agent_id": self.agent_id,
            "task_id": str(self.task_id) if self.task_id else None,
            "dry_run": self.dry_run,
        }


@dataclass
class WriterConfig:
    """Configuration for repo writer."""
    base_path: Path = field(default_factory=lambda: Path.cwd())
    backup_enabled: bool = True
    backup_dir: str = "_backups"
    create_directories: bool = True
    dry_run: bool = False
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list[str] = field(default_factory=list)
    forbidden_paths: list[str] = field(default_factory=lambda: [".git", "node_modules", "__pycache__"])
    atomic_transactions: bool = True
    emit_packets: bool = True
    verify_checksums: bool = True


# =============================================================================
# Repository Writer
# =============================================================================

class RepoWriter:
    """
    Safe write operations for deterministic, resumable execution.
    
    Features:
    - Safe write operations with validation
    - Dry-run mode for preview
    - Atomic apply (all-or-nothing transactions)
    - Rollback support
    - Automatic backup
    - PacketEnvelope emission
    """
    
    def __init__(self, config: Optional[WriterConfig] = None):
        """
        Initialize the repo writer.
        
        Args:
            config: Writer configuration
        """
        self._config = config or WriterConfig()
        self._write_history: list[WriteResult] = []
        self._transactions: dict[UUID, WriteTransaction] = {}
        self._active_transaction: Optional[WriteTransaction] = None
        self._packet_emitter: Optional[Callable] = None
        self._lock = asyncio.Lock()
        
        logger.info(f"RepoWriter initialized (base_path={self._config.base_path})")
    
    def set_packet_emitter(self, emitter: Callable) -> None:
        """Set the packet emitter function."""
        self._packet_emitter = emitter
    
    # ==========================================================================
    # Simple Write Operations
    # ==========================================================================
    
    def write_file(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        dry_run: Optional[bool] = None,
    ) -> WriteResult:
        """
        Write content to a file.
        
        Args:
            path: Relative path to file
            content: Content to write
            encoding: Text encoding
            dry_run: Override config dry_run setting
            
        Returns:
            WriteResult
        """
        is_dry_run = dry_run if dry_run is not None else self._config.dry_run
        result = WriteResult(path=path, operation_type=WriteOperationType.CREATE, dry_run=is_dry_run)
        
        try:
            full_path = self._resolve_path(path)
            
            # Validate
            if not self._validate_path(full_path, result):
                return result
            
            content_bytes = content.encode(encoding)
            if len(content_bytes) > self._config.max_file_size_bytes:
                result.error = f"Content exceeds max size ({self._config.max_file_size_bytes} bytes)"
                return result
            
            # Calculate checksum
            result.checksum = hashlib.sha256(content_bytes).hexdigest()
            result.bytes_written = len(content_bytes)
            
            # Dry run - don't actually write
            if is_dry_run:
                result.success = True
                result.operation_type = WriteOperationType.UPDATE if full_path.exists() else WriteOperationType.CREATE
                logger.info(f"[DRY RUN] Would write {result.bytes_written} bytes to {path}")
                self._write_history.append(result)
                return result
            
            # Backup existing
            if self._config.backup_enabled and full_path.exists():
                backup_path = self._create_backup(full_path)
                result.backup_path = str(backup_path)
                result.operation_type = WriteOperationType.UPDATE
            
            # Create directories
            if self._config.create_directories:
                full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write atomically (write to temp, then rename)
            temp_path = full_path.with_suffix(full_path.suffix + ".tmp")
            
            with open(temp_path, "w", encoding=encoding) as f:
                f.write(content)
            
            temp_path.rename(full_path)
            
            result.success = True
            logger.info(f"Wrote {result.bytes_written} bytes to {path}")
            
        except Exception as e:
            logger.error(f"Write failed for {path}: {e}")
            result.error = str(e)
        
        self._write_history.append(result)
        return result
    
    def write_binary(
        self,
        path: str,
        content: bytes,
        dry_run: Optional[bool] = None,
    ) -> WriteResult:
        """
        Write binary content to a file.
        
        Args:
            path: Relative path to file
            content: Binary content
            dry_run: Override config dry_run setting
            
        Returns:
            WriteResult
        """
        is_dry_run = dry_run if dry_run is not None else self._config.dry_run
        result = WriteResult(path=path, operation_type=WriteOperationType.CREATE, dry_run=is_dry_run)
        
        try:
            full_path = self._resolve_path(path)
            
            if not self._validate_path(full_path, result):
                return result
            
            if len(content) > self._config.max_file_size_bytes:
                result.error = f"Content exceeds max size"
                return result
            
            result.checksum = hashlib.sha256(content).hexdigest()
            result.bytes_written = len(content)
            
            if is_dry_run:
                result.success = True
                logger.info(f"[DRY RUN] Would write {result.bytes_written} binary bytes to {path}")
                self._write_history.append(result)
                return result
            
            if self._config.backup_enabled and full_path.exists():
                result.backup_path = str(self._create_backup(full_path))
                result.operation_type = WriteOperationType.UPDATE
            
            if self._config.create_directories:
                full_path.parent.mkdir(parents=True, exist_ok=True)
            
            temp_path = full_path.with_suffix(full_path.suffix + ".tmp")
            
            with open(temp_path, "wb") as f:
                f.write(content)
            
            temp_path.rename(full_path)
            
            result.success = True
            
        except Exception as e:
            result.error = str(e)
        
        self._write_history.append(result)
        return result
    
    def write_files(
        self,
        files: dict[str, str],
        encoding: str = "utf-8",
        dry_run: Optional[bool] = None,
        atomic: bool = True,
    ) -> list[WriteResult]:
        """
        Write multiple files.
        
        Args:
            files: Dict of path -> content
            encoding: Text encoding
            dry_run: Override config dry_run setting
            atomic: If True, all writes succeed or all fail
            
        Returns:
            List of WriteResults
        """
        if atomic and not (dry_run if dry_run is not None else self._config.dry_run):
            return self._write_files_atomic(files, encoding)
        
        results = []
        for path, content in files.items():
            result = self.write_file(path, content, encoding, dry_run)
            results.append(result)
        return results
    
    def _write_files_atomic(
        self,
        files: dict[str, str],
        encoding: str = "utf-8",
    ) -> list[WriteResult]:
        """Write files atomically - all succeed or all fail."""
        results = []
        written_paths = []
        backup_mapping: dict[str, str] = {}  # path -> backup_path
        
        try:
            for path, content in files.items():
                full_path = self._resolve_path(path)
                result = WriteResult(path=path, operation_type=WriteOperationType.CREATE)
                
                if not self._validate_path(full_path, result):
                    raise ValueError(result.error)
                
                content_bytes = content.encode(encoding)
                result.checksum = hashlib.sha256(content_bytes).hexdigest()
                result.bytes_written = len(content_bytes)
                
                # Backup existing
                if full_path.exists():
                    backup_path = self._create_backup(full_path)
                    backup_mapping[path] = str(backup_path)
                    result.backup_path = str(backup_path)
                    result.operation_type = WriteOperationType.UPDATE
                
                # Create directories
                if self._config.create_directories:
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write atomically
                temp_path = full_path.with_suffix(full_path.suffix + ".tmp")
                
                with open(temp_path, "w", encoding=encoding) as f:
                    f.write(content)
                
                temp_path.rename(full_path)
                written_paths.append(full_path)
                
                result.success = True
                results.append(result)
            
            logger.info(f"Atomic write: {len(written_paths)} files written successfully")
            
        except Exception as e:
            logger.error(f"Atomic write failed: {e}")
            
            # Rollback all written files
            for full_path in written_paths:
                try:
                    rel_path = str(full_path.relative_to(self._config.base_path))
                    backup_path = backup_mapping.get(rel_path)
                    
                    if backup_path:
                        # Restore from backup
                        shutil.copy2(backup_path, full_path)
                    else:
                        # Remove newly created file
                        full_path.unlink()
                except Exception as rollback_error:
                    logger.error(f"Rollback failed for {full_path}: {rollback_error}")
            
            # Mark all results as failed
            for result in results:
                result.success = False
                result.error = str(e)
        
        for result in results:
            self._write_history.append(result)
        
        return results
    
    # ==========================================================================
    # Directory Operations
    # ==========================================================================
    
    def create_directory(self, path: str, dry_run: Optional[bool] = None) -> WriteResult:
        """
        Create a directory.
        
        Args:
            path: Directory path
            dry_run: Override config dry_run setting
            
        Returns:
            WriteResult
        """
        is_dry_run = dry_run if dry_run is not None else self._config.dry_run
        result = WriteResult(path=path, operation_type=WriteOperationType.MKDIR, dry_run=is_dry_run)
        
        try:
            full_path = self._resolve_path(path)
            
            if is_dry_run:
                result.success = True
                logger.info(f"[DRY RUN] Would create directory {path}")
                return result
            
            full_path.mkdir(parents=True, exist_ok=True)
            result.success = True
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    def delete_file(
        self,
        path: str,
        backup: bool = True,
        dry_run: Optional[bool] = None,
    ) -> WriteResult:
        """
        Delete a file.
        
        Args:
            path: File path
            backup: Whether to backup before deleting
            dry_run: Override config dry_run setting
            
        Returns:
            WriteResult
        """
        is_dry_run = dry_run if dry_run is not None else self._config.dry_run
        result = WriteResult(path=path, operation_type=WriteOperationType.DELETE, dry_run=is_dry_run)
        
        try:
            full_path = self._resolve_path(path)
            
            if not full_path.exists():
                result.error = "File not found"
                return result
            
            if is_dry_run:
                result.success = True
                logger.info(f"[DRY RUN] Would delete {path}")
                return result
            
            if backup and self._config.backup_enabled:
                result.backup_path = str(self._create_backup(full_path))
            
            full_path.unlink()
            result.success = True
            
        except Exception as e:
            result.error = str(e)
        
        self._write_history.append(result)
        return result
    
    def rename_file(
        self,
        old_path: str,
        new_path: str,
        dry_run: Optional[bool] = None,
    ) -> WriteResult:
        """
        Rename/move a file.
        
        Args:
            old_path: Current file path
            new_path: New file path
            dry_run: Override config dry_run setting
            
        Returns:
            WriteResult
        """
        is_dry_run = dry_run if dry_run is not None else self._config.dry_run
        result = WriteResult(path=old_path, operation_type=WriteOperationType.RENAME, dry_run=is_dry_run)
        
        try:
            old_full_path = self._resolve_path(old_path)
            new_full_path = self._resolve_path(new_path)
            
            if not old_full_path.exists():
                result.error = "Source file not found"
                return result
            
            if new_full_path.exists():
                result.error = "Target file already exists"
                return result
            
            if is_dry_run:
                result.success = True
                logger.info(f"[DRY RUN] Would rename {old_path} to {new_path}")
                return result
            
            # Create target directory if needed
            if self._config.create_directories:
                new_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            old_full_path.rename(new_full_path)
            result.success = True
            result.path = new_path
            
        except Exception as e:
            result.error = str(e)
        
        self._write_history.append(result)
        return result
    
    # ==========================================================================
    # Transaction Management
    # ==========================================================================
    
    def begin_transaction(
        self,
        description: str = "",
        agent_id: Optional[str] = None,
        task_id: Optional[UUID] = None,
        dry_run: Optional[bool] = None,
    ) -> WriteTransaction:
        """
        Begin a new transaction.
        
        Args:
            description: Transaction description
            agent_id: Agent ID
            task_id: Task ID
            dry_run: Override config dry_run setting
            
        Returns:
            WriteTransaction
        """
        if self._active_transaction and self._active_transaction.status == TransactionStatus.IN_PROGRESS:
            raise RuntimeError("Another transaction is in progress")
        
        transaction = WriteTransaction(
            description=description,
            agent_id=agent_id,
            task_id=task_id,
            dry_run=dry_run if dry_run is not None else self._config.dry_run,
        )
        
        self._transactions[transaction.transaction_id] = transaction
        self._active_transaction = transaction
        
        logger.info(f"Transaction started: {transaction.transaction_id}")
        
        return transaction
    
    def add_operation(
        self,
        operation_type: WriteOperationType,
        path: str,
        content: Optional[Union[str, bytes]] = None,
        new_path: Optional[str] = None,
        encoding: str = "utf-8",
        is_binary: bool = False,
    ) -> WriteOperation:
        """
        Add an operation to the current transaction.
        
        Args:
            operation_type: Type of operation
            path: File path
            content: Content (for create/update)
            new_path: New path (for rename/move)
            encoding: Text encoding
            is_binary: Whether content is binary
            
        Returns:
            WriteOperation
        """
        if not self._active_transaction:
            raise RuntimeError("No active transaction")
        
        operation = WriteOperation(
            operation_type=operation_type,
            path=path,
            content=content,
            new_path=new_path,
            encoding=encoding,
            is_binary=is_binary,
        )
        
        self._active_transaction.operations.append(operation)
        
        return operation
    
    async def commit_transaction(
        self,
        transaction_id: Optional[UUID] = None,
    ) -> list[WriteResult]:
        """
        Commit a transaction.
        
        Args:
            transaction_id: Transaction ID (uses active if not provided)
            
        Returns:
            List of WriteResults
        """
        async with self._lock:
            transaction = None
            
            if transaction_id:
                transaction = self._transactions.get(transaction_id)
            else:
                transaction = self._active_transaction
            
            if not transaction:
                raise RuntimeError("Transaction not found")
            
            transaction.status = TransactionStatus.IN_PROGRESS
            transaction.started_at = datetime.utcnow()
            
            results = []
            executed_operations: list[WriteOperation] = []
            
            try:
                for operation in transaction.operations:
                    result = self._execute_operation(operation, transaction.dry_run)
                    results.append(result)
                    operation.executed = True
                    operation.success = result.success
                    
                    if result.success:
                        executed_operations.append(operation)
                    elif self._config.atomic_transactions:
                        # Rollback on failure in atomic mode
                        raise RuntimeError(f"Operation failed: {result.error}")
                
                transaction.status = TransactionStatus.COMMITTED
                transaction.committed_at = datetime.utcnow()
                transaction.results = results
                
                logger.info(f"Transaction committed: {transaction.transaction_id}")
                
            except Exception as e:
                logger.error(f"Transaction failed: {e}")
                
                # Rollback executed operations
                if self._config.atomic_transactions:
                    self._rollback_operations(executed_operations)
                
                transaction.status = TransactionStatus.FAILED
                
                for result in results:
                    if result.success:
                        result.success = False
                        result.error = f"Rolled back: {str(e)}"
            
            finally:
                if self._active_transaction == transaction:
                    self._active_transaction = None
            
            return results
    
    async def rollback_transaction(
        self,
        transaction_id: Optional[UUID] = None,
    ) -> bool:
        """
        Rollback a transaction.
        
        Args:
            transaction_id: Transaction ID (uses active if not provided)
            
        Returns:
            True if rolled back
        """
        async with self._lock:
            transaction = None
            
            if transaction_id:
                transaction = self._transactions.get(transaction_id)
            else:
                transaction = self._active_transaction
            
            if not transaction:
                return False
            
            # Only rollback if committed or in progress
            if transaction.status not in (TransactionStatus.COMMITTED, TransactionStatus.IN_PROGRESS):
                return False
            
            # Get executed operations that succeeded
            executed = [op for op in transaction.operations if op.executed and op.success]
            
            self._rollback_operations(executed)
            
            transaction.status = TransactionStatus.ROLLED_BACK
            transaction.rolled_back_at = datetime.utcnow()
            
            if self._active_transaction == transaction:
                self._active_transaction = None
            
            logger.info(f"Transaction rolled back: {transaction.transaction_id}")
            
            return True
    
    def _execute_operation(
        self,
        operation: WriteOperation,
        dry_run: bool,
    ) -> WriteResult:
        """Execute a single write operation."""
        if operation.operation_type == WriteOperationType.CREATE:
            if operation.is_binary:
                return self.write_binary(operation.path, operation.content, dry_run)
            else:
                return self.write_file(operation.path, operation.content, operation.encoding, dry_run)
        
        elif operation.operation_type == WriteOperationType.UPDATE:
            if operation.is_binary:
                return self.write_binary(operation.path, operation.content, dry_run)
            else:
                return self.write_file(operation.path, operation.content, operation.encoding, dry_run)
        
        elif operation.operation_type == WriteOperationType.DELETE:
            return self.delete_file(operation.path, backup=True, dry_run=dry_run)
        
        elif operation.operation_type == WriteOperationType.RENAME:
            return self.rename_file(operation.path, operation.new_path, dry_run)
        
        elif operation.operation_type == WriteOperationType.MOVE:
            return self.rename_file(operation.path, operation.new_path, dry_run)
        
        elif operation.operation_type == WriteOperationType.MKDIR:
            return self.create_directory(operation.path, dry_run)
        
        return WriteResult(path=operation.path, error="Unknown operation type")
    
    def _rollback_operations(self, operations: list[WriteOperation]) -> None:
        """Rollback a list of operations."""
        # Reverse order for proper rollback
        for operation in reversed(operations):
            try:
                full_path = self._resolve_path(operation.path)
                
                if operation.operation_type in (WriteOperationType.CREATE, WriteOperationType.UPDATE):
                    if operation.backup_content is not None:
                        # Restore from backup
                        if operation.is_binary:
                            with open(full_path, "wb") as f:
                                f.write(operation.backup_content)
                        else:
                            with open(full_path, "w", encoding=operation.encoding) as f:
                                f.write(operation.backup_content)
                    elif not operation.backup_existed:
                        # File didn't exist before, remove it
                        if full_path.exists():
                            full_path.unlink()
                
                elif operation.operation_type == WriteOperationType.DELETE:
                    if operation.backup_content is not None:
                        # Restore deleted file
                        if operation.is_binary:
                            with open(full_path, "wb") as f:
                                f.write(operation.backup_content)
                        else:
                            with open(full_path, "w", encoding=operation.encoding) as f:
                                f.write(operation.backup_content)
                
                elif operation.operation_type in (WriteOperationType.RENAME, WriteOperationType.MOVE):
                    if operation.new_path:
                        # Reverse the rename/move
                        new_full_path = self._resolve_path(operation.new_path)
                        if new_full_path.exists():
                            new_full_path.rename(full_path)
                
                logger.debug(f"Rolled back: {operation.path}")
                
            except Exception as e:
                logger.error(f"Rollback failed for {operation.path}: {e}")
    
    # ==========================================================================
    # Rollback Support
    # ==========================================================================
    
    def rollback_write(self, result: WriteResult) -> WriteResult:
        """
        Rollback a single write operation.
        
        Args:
            result: WriteResult to rollback
            
        Returns:
            WriteResult of rollback operation
        """
        rollback_result = WriteResult(path=result.path)
        
        try:
            if not result.backup_path:
                rollback_result.error = "No backup available"
                return rollback_result
            
            backup_path = Path(result.backup_path)
            target_path = self._resolve_path(result.path)
            
            if not backup_path.exists():
                rollback_result.error = "Backup file not found"
                return rollback_result
            
            # Restore from backup
            shutil.copy2(backup_path, target_path)
            
            rollback_result.success = True
            logger.info(f"Rolled back {result.path} from backup")
            
        except Exception as e:
            rollback_result.error = str(e)
        
        return rollback_result
    
    def restore_backup(self, backup_path: str, target_path: str) -> WriteResult:
        """
        Restore a file from backup.
        
        Args:
            backup_path: Path to backup file
            target_path: Where to restore
            
        Returns:
            WriteResult
        """
        result = WriteResult(path=target_path)
        
        try:
            backup_full = self._resolve_path(backup_path)
            target_full = self._resolve_path(target_path)
            
            if not backup_full.exists():
                result.error = f"Backup not found: {backup_path}"
                return result
            
            if self._config.dry_run:
                result.success = True
                result.dry_run = True
                return result
            
            shutil.copy2(backup_full, target_full)
            result.success = True
            result.bytes_written = backup_full.stat().st_size
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    # ==========================================================================
    # Backup Management
    # ==========================================================================
    
    def _create_backup(self, path: Path) -> Path:
        """Create a backup of a file."""
        backup_dir = self._config.base_path / self._config.backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        backup_name = f"{path.stem}_{timestamp}{path.suffix}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(path, backup_path)
        
        logger.debug(f"Created backup: {backup_path}")
        return backup_path
    
    def list_backups(self, pattern: str = "*") -> list[Path]:
        """
        List backup files.
        
        Args:
            pattern: Glob pattern for filtering
            
        Returns:
            List of backup file paths
        """
        backup_dir = self._config.base_path / self._config.backup_dir
        if not backup_dir.exists():
            return []
        
        return list(backup_dir.glob(pattern))
    
    def cleanup_backups(self, max_age_hours: int = 24) -> int:
        """
        Clean up old backups.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of backups removed
        """
        backup_dir = self._config.base_path / self._config.backup_dir
        if not backup_dir.exists():
            return 0
        
        cutoff = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        removed = 0
        
        for backup_file in backup_dir.iterdir():
            if backup_file.stat().st_mtime < cutoff:
                backup_file.unlink()
                removed += 1
        
        logger.info(f"Cleaned up {removed} old backups")
        return removed
    
    # ==========================================================================
    # Utility
    # ==========================================================================
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve a path relative to base."""
        return self._config.base_path / path
    
    def _validate_path(self, path: Path, result: WriteResult) -> bool:
        """Validate a path for writing."""
        # Check if within base
        try:
            path.relative_to(self._config.base_path)
        except ValueError:
            result.error = "Path outside base directory"
            return False
        
        # Check forbidden paths
        path_str = str(path)
        for forbidden in self._config.forbidden_paths:
            if forbidden in path_str:
                result.error = f"Path contains forbidden component: {forbidden}"
                return False
        
        # Check extension
        if self._config.allowed_extensions:
            if path.suffix not in self._config.allowed_extensions:
                result.error = f"Extension {path.suffix} not allowed"
                return False
        
        return True
    
    def get_write_history(self, limit: int = 100) -> list[WriteResult]:
        """Get recent write history."""
        return self._write_history[-limit:]
    
    def set_base_path(self, path: Path) -> None:
        """Update base path."""
        self._config.base_path = path
        logger.info(f"Base path updated to {path}")
    
    def set_dry_run(self, enabled: bool) -> None:
        """Enable or disable dry-run mode."""
        self._config.dry_run = enabled
        logger.info(f"Dry-run mode: {enabled}")
    
    def get_transaction(self, transaction_id: UUID) -> Optional[WriteTransaction]:
        """Get a transaction by ID."""
        return self._transactions.get(transaction_id)
    
    def get_active_transaction(self) -> Optional[WriteTransaction]:
        """Get the currently active transaction."""
        return self._active_transaction
