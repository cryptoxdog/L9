"""
L9 Runtime - Repository Reader
==============================
Version: 2.0.0

Safe file reading with diff and code block extraction.

Features:
- Safe file reading
- Content caching
- File diff generation
- Code block extraction
- Pattern matching
- Structure analysis
- PacketEnvelope emission

Compatibility:
- Memory substrate (PacketEnvelope v1.1.0)
- World model integration
- IR Engine integration
"""

from __future__ import annotations

import difflib
import fnmatch
import hashlib
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Callable, Iterator
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class ReadResult:
    """Result of a read operation."""
    read_id: UUID = field(default_factory=uuid4)
    path: str = ""
    success: bool = False
    content: Optional[str] = None
    binary_content: Optional[bytes] = None
    size_bytes: int = 0
    encoding: str = "utf-8"
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None
    line_count: int = 0
    from_cache: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "read_id": str(self.read_id),
            "path": self.path,
            "success": self.success,
            "size_bytes": self.size_bytes,
            "encoding": self.encoding,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "checksum": self.checksum,
            "line_count": self.line_count,
            "from_cache": self.from_cache,
        }


@dataclass
class FileInfo:
    """Information about a file."""
    path: str
    name: str
    extension: str
    size_bytes: int
    is_directory: bool
    modified_at: datetime
    checksum: Optional[str] = None
    line_count: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "path": self.path,
            "name": self.name,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "is_directory": self.is_directory,
            "modified_at": self.modified_at.isoformat(),
            "checksum": self.checksum,
            "line_count": self.line_count,
        }


@dataclass
class DiffResult:
    """Result of a diff operation."""
    diff_id: UUID = field(default_factory=uuid4)
    source_path: str = ""
    target_path: str = ""
    diff_type: str = "unified"  # unified, context, html
    diff_lines: list[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    is_identical: bool = False
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "diff_id": str(self.diff_id),
            "source_path": self.source_path,
            "target_path": self.target_path,
            "diff_type": self.diff_type,
            "additions": self.additions,
            "deletions": self.deletions,
            "changes": self.changes,
            "is_identical": self.is_identical,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def get_diff_text(self) -> str:
        """Get diff as text."""
        return "\n".join(self.diff_lines)
    
    def get_summary(self) -> str:
        """Get summary of changes."""
        if self.is_identical:
            return "Files are identical"
        return f"+{self.additions} -{self.deletions} ~{self.changes}"


@dataclass
class CodeBlock:
    """An extracted code block."""
    block_id: UUID = field(default_factory=uuid4)
    path: str = ""
    language: str = ""
    start_line: int = 0
    end_line: int = 0
    content: str = ""
    block_type: str = ""  # function, class, method, import, etc.
    name: Optional[str] = None
    parent_name: Optional[str] = None
    signature: Optional[str] = None
    docstring: Optional[str] = None
    indentation: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "block_id": str(self.block_id),
            "path": self.path,
            "language": self.language,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "content": self.content,
            "block_type": self.block_type,
            "name": self.name,
            "parent_name": self.parent_name,
            "signature": self.signature,
            "docstring": self.docstring,
            "indentation": self.indentation,
        }
    
    @property
    def line_count(self) -> int:
        """Number of lines in block."""
        return self.end_line - self.start_line + 1


@dataclass
class SearchResult:
    """Result of a search operation."""
    search_id: UUID = field(default_factory=uuid4)
    query: str = ""
    pattern_type: str = "text"  # text, regex, glob
    matches: list[dict[str, Any]] = field(default_factory=list)
    files_searched: int = 0
    files_matched: int = 0
    total_matches: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "search_id": str(self.search_id),
            "query": self.query,
            "pattern_type": self.pattern_type,
            "files_searched": self.files_searched,
            "files_matched": self.files_matched,
            "total_matches": self.total_matches,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReaderConfig:
    """Configuration for repo reader."""
    base_path: Path = field(default_factory=lambda: Path.cwd())
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10MB
    cache_enabled: bool = True
    cache_max_size: int = 100
    ignore_patterns: list[str] = field(default_factory=lambda: [
        "*.pyc", "__pycache__", ".git", "node_modules", ".env",
        "*.lock", "*.log", ".DS_Store",
    ])
    binary_extensions: list[str] = field(default_factory=lambda: [
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf",
        ".zip", ".tar", ".gz", ".exe", ".dll", ".so",
    ])
    emit_packets: bool = True


# =============================================================================
# Code Block Patterns
# =============================================================================

# Python patterns
PYTHON_PATTERNS = {
    "function": re.compile(r"^(\s*)def\s+(\w+)\s*\(", re.MULTILINE),
    "async_function": re.compile(r"^(\s*)async\s+def\s+(\w+)\s*\(", re.MULTILINE),
    "class": re.compile(r"^(\s*)class\s+(\w+)\s*[\(:]", re.MULTILINE),
    "import": re.compile(r"^(from\s+[\w.]+\s+import\s+.+|import\s+.+)$", re.MULTILINE),
    "decorator": re.compile(r"^(\s*)@(\w+)", re.MULTILINE),
}

# JavaScript/TypeScript patterns
JS_PATTERNS = {
    "function": re.compile(r"^(\s*)(function|async\s+function)\s+(\w+)\s*\(", re.MULTILINE),
    "arrow_function": re.compile(r"^(\s*)(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(", re.MULTILINE),
    "class": re.compile(r"^(\s*)class\s+(\w+)", re.MULTILINE),
    "method": re.compile(r"^(\s*)(?:async\s+)?(\w+)\s*\([^)]*\)\s*{", re.MULTILINE),
    "import": re.compile(r"^(import\s+.+|const\s+.+\s*=\s*require\(.+\))$", re.MULTILINE),
    "export": re.compile(r"^export\s+(default\s+)?(function|class|const|let|var)", re.MULTILINE),
}


# =============================================================================
# Repository Reader
# =============================================================================

class RepoReader:
    """
    Safe file reading with diff and code block extraction.
    
    Features:
    - Content caching
    - File/directory listing
    - Pattern-based search
    - File diff generation
    - Code block extraction
    - Structure analysis
    """
    
    def __init__(self, config: Optional[ReaderConfig] = None):
        """
        Initialize the repo reader.
        
        Args:
            config: Reader configuration
        """
        self._config = config or ReaderConfig()
        self._cache: dict[str, tuple[str, datetime, str]] = {}  # path -> (content, cached_at, checksum)
        self._packet_emitter: Optional[Callable] = None
        
        logger.info(f"RepoReader initialized (base_path={self._config.base_path})")
    
    def set_packet_emitter(self, emitter: Callable) -> None:
        """Set the packet emitter function."""
        self._packet_emitter = emitter
    
    # ==========================================================================
    # Read Operations
    # ==========================================================================
    
    def read_file(
        self,
        path: str,
        encoding: str = "utf-8",
        use_cache: bool = True,
    ) -> ReadResult:
        """
        Read a text file.
        
        Args:
            path: Relative path to file
            encoding: Text encoding
            use_cache: Whether to use cache
            
        Returns:
            ReadResult
        """
        result = ReadResult(path=path, encoding=encoding)
        
        try:
            full_path = self._resolve_path(path)
            
            if not full_path.exists():
                result.error = "File not found"
                return result
            
            if full_path.is_dir():
                result.error = "Path is a directory"
                return result
            
            # Check size
            size = full_path.stat().st_size
            if size > self._config.max_file_size_bytes:
                result.error = f"File too large ({size} bytes)"
                return result
            
            result.size_bytes = size
            
            # Check cache
            if use_cache and self._config.cache_enabled and path in self._cache:
                content, cached_at, checksum = self._cache[path]
                file_mtime = datetime.fromtimestamp(full_path.stat().st_mtime)
                
                if cached_at >= file_mtime:
                    result.success = True
                    result.content = content
                    result.checksum = checksum
                    result.line_count = content.count("\n") + 1
                    result.from_cache = True
                    return result
            
            # Read file
            with open(full_path, "r", encoding=encoding) as f:
                content = f.read()
            
            # Calculate checksum
            checksum = hashlib.sha256(content.encode(encoding)).hexdigest()
            
            result.success = True
            result.content = content
            result.checksum = checksum
            result.line_count = content.count("\n") + 1
            
            # Update cache
            if self._config.cache_enabled:
                self._update_cache(path, content, checksum)
            
        except UnicodeDecodeError:
            result.error = f"Unable to decode file with {encoding} encoding"
        except Exception as e:
            result.error = str(e)
        
        return result
    
    def read_binary(self, path: str) -> ReadResult:
        """
        Read a binary file.
        
        Args:
            path: Relative path to file
            
        Returns:
            ReadResult
        """
        result = ReadResult(path=path)
        
        try:
            full_path = self._resolve_path(path)
            
            if not full_path.exists():
                result.error = "File not found"
                return result
            
            size = full_path.stat().st_size
            if size > self._config.max_file_size_bytes:
                result.error = f"File too large ({size} bytes)"
                return result
            
            with open(full_path, "rb") as f:
                content = f.read()
            
            result.success = True
            result.binary_content = content
            result.size_bytes = len(content)
            result.checksum = hashlib.sha256(content).hexdigest()
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    def read_files(
        self,
        paths: list[str],
        encoding: str = "utf-8",
    ) -> dict[str, ReadResult]:
        """
        Read multiple files.
        
        Args:
            paths: List of paths
            encoding: Text encoding
            
        Returns:
            Dict of path -> ReadResult
        """
        return {path: self.read_file(path, encoding) for path in paths}
    
    def read_lines(
        self,
        path: str,
        start_line: int = 1,
        end_line: Optional[int] = None,
        encoding: str = "utf-8",
    ) -> ReadResult:
        """
        Read specific lines from a file.
        
        Args:
            path: File path
            start_line: Starting line (1-indexed)
            end_line: Ending line (inclusive, None for end of file)
            encoding: Text encoding
            
        Returns:
            ReadResult with selected lines
        """
        result = self.read_file(path, encoding)
        
        if not result.success or not result.content:
            return result
        
        lines = result.content.splitlines(keepends=True)
        
        # Adjust to 0-indexed
        start_idx = max(0, start_line - 1)
        end_idx = end_line if end_line else len(lines)
        
        result.content = "".join(lines[start_idx:end_idx])
        result.line_count = end_idx - start_idx
        
        return result
    
    # ==========================================================================
    # File Diff
    # ==========================================================================
    
    def diff_files(
        self,
        source_path: str,
        target_path: str,
        diff_type: str = "unified",
        context_lines: int = 3,
    ) -> DiffResult:
        """
        Generate diff between two files.
        
        Args:
            source_path: Source file path
            target_path: Target file path
            diff_type: Type of diff (unified, context, html)
            context_lines: Number of context lines
            
        Returns:
            DiffResult
        """
        result = DiffResult(
            source_path=source_path,
            target_path=target_path,
            diff_type=diff_type,
        )
        
        try:
            source_result = self.read_file(source_path)
            target_result = self.read_file(target_path)
            
            if not source_result.success:
                result.error = f"Cannot read source: {source_result.error}"
                return result
            
            if not target_result.success:
                result.error = f"Cannot read target: {target_result.error}"
                return result
            
            source_lines = source_result.content.splitlines(keepends=True)
            target_lines = target_result.content.splitlines(keepends=True)
            
            # Generate diff
            if diff_type == "unified":
                diff = difflib.unified_diff(
                    source_lines,
                    target_lines,
                    fromfile=source_path,
                    tofile=target_path,
                    n=context_lines,
                )
            elif diff_type == "context":
                diff = difflib.context_diff(
                    source_lines,
                    target_lines,
                    fromfile=source_path,
                    tofile=target_path,
                    n=context_lines,
                )
            elif diff_type == "html":
                differ = difflib.HtmlDiff()
                html = differ.make_file(
                    source_lines,
                    target_lines,
                    fromdesc=source_path,
                    todesc=target_path,
                    context=True,
                    numlines=context_lines,
                )
                result.diff_lines = [html]
                result.is_identical = source_result.content == target_result.content
                return result
            else:
                result.error = f"Unknown diff type: {diff_type}"
                return result
            
            result.diff_lines = list(diff)
            
            # Count changes
            for line in result.diff_lines:
                if line.startswith("+") and not line.startswith("+++"):
                    result.additions += 1
                elif line.startswith("-") and not line.startswith("---"):
                    result.deletions += 1
            
            result.changes = result.additions + result.deletions
            result.is_identical = source_result.content == target_result.content
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    def diff_content(
        self,
        source_content: str,
        target_content: str,
        source_name: str = "source",
        target_name: str = "target",
        context_lines: int = 3,
    ) -> DiffResult:
        """
        Generate diff between two content strings.
        
        Args:
            source_content: Source content
            target_content: Target content
            source_name: Name for source
            target_name: Name for target
            context_lines: Number of context lines
            
        Returns:
            DiffResult
        """
        result = DiffResult(
            source_path=source_name,
            target_path=target_name,
        )
        
        try:
            source_lines = source_content.splitlines(keepends=True)
            target_lines = target_content.splitlines(keepends=True)
            
            diff = difflib.unified_diff(
                source_lines,
                target_lines,
                fromfile=source_name,
                tofile=target_name,
                n=context_lines,
            )
            
            result.diff_lines = list(diff)
            
            for line in result.diff_lines:
                if line.startswith("+") and not line.startswith("+++"):
                    result.additions += 1
                elif line.startswith("-") and not line.startswith("---"):
                    result.deletions += 1
            
            result.changes = result.additions + result.deletions
            result.is_identical = source_content == target_content
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    def get_file_changes(
        self,
        original_content: str,
        modified_content: str,
    ) -> list[dict[str, Any]]:
        """
        Get detailed list of changes between two contents.
        
        Args:
            original_content: Original content
            modified_content: Modified content
            
        Returns:
            List of change dictionaries
        """
        changes = []
        
        original_lines = original_content.splitlines()
        modified_lines = modified_content.splitlines()
        
        differ = difflib.SequenceMatcher(None, original_lines, modified_lines)
        
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == "equal":
                continue
            
            change = {
                "type": tag,
                "original_start": i1 + 1,
                "original_end": i2,
                "modified_start": j1 + 1,
                "modified_end": j2,
            }
            
            if tag == "replace":
                change["original_lines"] = original_lines[i1:i2]
                change["modified_lines"] = modified_lines[j1:j2]
            elif tag == "delete":
                change["original_lines"] = original_lines[i1:i2]
            elif tag == "insert":
                change["modified_lines"] = modified_lines[j1:j2]
            
            changes.append(change)
        
        return changes
    
    # ==========================================================================
    # Code Block Extraction
    # ==========================================================================
    
    def extract_code_blocks(
        self,
        path: str,
        block_types: Optional[list[str]] = None,
    ) -> list[CodeBlock]:
        """
        Extract code blocks from a file.
        
        Args:
            path: File path
            block_types: Types to extract (function, class, etc.)
            
        Returns:
            List of CodeBlocks
        """
        result = self.read_file(path)
        if not result.success or not result.content:
            return []
        
        # Detect language
        extension = Path(path).suffix.lower()
        
        if extension in (".py",):
            return self._extract_python_blocks(path, result.content, block_types)
        elif extension in (".js", ".ts", ".jsx", ".tsx"):
            return self._extract_js_blocks(path, result.content, block_types)
        else:
            return self._extract_generic_blocks(path, result.content, block_types)
    
    def _extract_python_blocks(
        self,
        path: str,
        content: str,
        block_types: Optional[list[str]],
    ) -> list[CodeBlock]:
        """Extract code blocks from Python file."""
        blocks = []
        lines = content.splitlines()
        
        # Extract functions and classes
        for pattern_name, pattern in PYTHON_PATTERNS.items():
            if block_types and pattern_name not in block_types:
                continue
            
            for match in pattern.finditer(content):
                start_pos = match.start()
                start_line = content[:start_pos].count("\n") + 1
                
                if pattern_name in ("function", "async_function"):
                    indentation = len(match.group(1))
                    name = match.group(2)
                    end_line = self._find_python_block_end(lines, start_line - 1, indentation)
                    
                    block_content = "\n".join(lines[start_line - 1:end_line])
                    signature = self._extract_python_signature(block_content)
                    docstring = self._extract_python_docstring(block_content)
                    
                    blocks.append(CodeBlock(
                        path=path,
                        language="python",
                        start_line=start_line,
                        end_line=end_line,
                        content=block_content,
                        block_type="function",
                        name=name,
                        signature=signature,
                        docstring=docstring,
                        indentation=indentation,
                    ))
                
                elif pattern_name == "class":
                    indentation = len(match.group(1))
                    name = match.group(2)
                    end_line = self._find_python_block_end(lines, start_line - 1, indentation)
                    
                    block_content = "\n".join(lines[start_line - 1:end_line])
                    docstring = self._extract_python_docstring(block_content)
                    
                    blocks.append(CodeBlock(
                        path=path,
                        language="python",
                        start_line=start_line,
                        end_line=end_line,
                        content=block_content,
                        block_type="class",
                        name=name,
                        docstring=docstring,
                        indentation=indentation,
                    ))
                
                elif pattern_name == "import":
                    blocks.append(CodeBlock(
                        path=path,
                        language="python",
                        start_line=start_line,
                        end_line=start_line,
                        content=match.group(0),
                        block_type="import",
                    ))
        
        return sorted(blocks, key=lambda b: b.start_line)
    
    def _find_python_block_end(
        self,
        lines: list[str],
        start_idx: int,
        base_indent: int,
    ) -> int:
        """Find the end of a Python block based on indentation."""
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            
            # Skip empty lines and comments
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            
            # Check indentation
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent and stripped:
                return i
        
        return len(lines)
    
    def _extract_python_signature(self, content: str) -> str:
        """Extract function signature from Python code."""
        match = re.search(r"^((?:async\s+)?def\s+\w+\s*\([^)]*\)(?:\s*->\s*[^:]+)?)", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_python_docstring(self, content: str) -> Optional[str]:
        """Extract docstring from Python code."""
        match = re.search(r'(?:def|class)\s+\w+[^:]*:\s*\n\s*(?:\'\'\'(.*?)\'\'\'|"""(.*?)""")', content, re.DOTALL)
        if match:
            return (match.group(1) or match.group(2)).strip()
        return None
    
    def _extract_js_blocks(
        self,
        path: str,
        content: str,
        block_types: Optional[list[str]],
    ) -> list[CodeBlock]:
        """Extract code blocks from JavaScript/TypeScript file."""
        blocks = []
        lines = content.splitlines()
        
        for pattern_name, pattern in JS_PATTERNS.items():
            if block_types and pattern_name not in block_types:
                continue
            
            for match in pattern.finditer(content):
                start_pos = match.start()
                start_line = content[:start_pos].count("\n") + 1
                
                # Find end of block by matching braces
                end_line = self._find_js_block_end(content, start_pos)
                end_line = content[:end_line].count("\n") + 1
                
                block_content = "\n".join(lines[start_line - 1:end_line])
                
                name = None
                if len(match.groups()) >= 2:
                    name = match.group(2) if match.group(2) else match.group(3) if len(match.groups()) >= 3 else None
                
                blocks.append(CodeBlock(
                    path=path,
                    language="javascript",
                    start_line=start_line,
                    end_line=end_line,
                    content=block_content,
                    block_type=pattern_name,
                    name=name,
                ))
        
        return sorted(blocks, key=lambda b: b.start_line)
    
    def _find_js_block_end(self, content: str, start_pos: int) -> int:
        """Find end of JS block by matching braces."""
        brace_count = 0
        in_string = False
        string_char = None
        
        for i in range(start_pos, len(content)):
            char = content[i]
            
            # Handle strings
            if char in ('"', "'", "`") and (i == 0 or content[i-1] != "\\"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                continue
            
            if in_string:
                continue
            
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    return i + 1
        
        return len(content)
    
    def _extract_generic_blocks(
        self,
        path: str,
        content: str,
        block_types: Optional[list[str]],
    ) -> list[CodeBlock]:
        """Extract generic code blocks (fallback)."""
        blocks = []
        lines = content.splitlines()
        
        # Simple function/method detection
        func_pattern = re.compile(r"^(\s*)(function|def|fn|func|sub|procedure)\s+(\w+)", re.MULTILINE)
        
        for match in func_pattern.finditer(content):
            start_pos = match.start()
            start_line = content[:start_pos].count("\n") + 1
            name = match.group(3)
            
            blocks.append(CodeBlock(
                path=path,
                language="unknown",
                start_line=start_line,
                end_line=start_line,  # Can't determine end reliably
                content=lines[start_line - 1] if start_line <= len(lines) else "",
                block_type="function",
                name=name,
            ))
        
        return blocks
    
    def extract_block_by_name(
        self,
        path: str,
        name: str,
        block_type: Optional[str] = None,
    ) -> Optional[CodeBlock]:
        """
        Extract a specific code block by name.
        
        Args:
            path: File path
            name: Block name
            block_type: Optional type filter
            
        Returns:
            CodeBlock or None
        """
        blocks = self.extract_code_blocks(path, [block_type] if block_type else None)
        
        for block in blocks:
            if block.name == name:
                return block
        
        return None
    
    def extract_blocks_by_pattern(
        self,
        path: str,
        pattern: str,
    ) -> list[CodeBlock]:
        """
        Extract code blocks matching a regex pattern.
        
        Args:
            path: File path
            pattern: Regex pattern for block names
            
        Returns:
            List of matching CodeBlocks
        """
        blocks = self.extract_code_blocks(path)
        regex = re.compile(pattern)
        
        return [b for b in blocks if b.name and regex.match(b.name)]
    
    # ==========================================================================
    # File Search
    # ==========================================================================
    
    def search_in_file(
        self,
        path: str,
        pattern: str,
        is_regex: bool = False,
        case_sensitive: bool = True,
    ) -> SearchResult:
        """
        Search for pattern in a file.
        
        Args:
            path: File path
            pattern: Search pattern
            is_regex: Whether pattern is regex
            case_sensitive: Case sensitivity
            
        Returns:
            SearchResult
        """
        result = SearchResult(
            query=pattern,
            pattern_type="regex" if is_regex else "text",
        )
        
        read_result = self.read_file(path)
        if not read_result.success or not read_result.content:
            return result
        
        result.files_searched = 1
        
        if is_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            for i, line in enumerate(read_result.content.splitlines(), 1):
                for match in regex.finditer(line):
                    result.matches.append({
                        "path": path,
                        "line_number": i,
                        "column": match.start() + 1,
                        "match": match.group(),
                        "line_content": line,
                    })
        else:
            search_pattern = pattern if case_sensitive else pattern.lower()
            
            for i, line in enumerate(read_result.content.splitlines(), 1):
                search_line = line if case_sensitive else line.lower()
                start = 0
                
                while True:
                    idx = search_line.find(search_pattern, start)
                    if idx == -1:
                        break
                    
                    result.matches.append({
                        "path": path,
                        "line_number": i,
                        "column": idx + 1,
                        "match": line[idx:idx + len(pattern)],
                        "line_content": line,
                    })
                    start = idx + 1
        
        result.total_matches = len(result.matches)
        if result.matches:
            result.files_matched = 1
        
        return result
    
    def search_files(
        self,
        pattern: str,
        path: str = "",
        file_pattern: str = "*",
        is_regex: bool = False,
        case_sensitive: bool = True,
        max_results: int = 1000,
    ) -> SearchResult:
        """
        Search for pattern across files.
        
        Args:
            pattern: Search pattern
            path: Directory to search
            file_pattern: Glob pattern for files
            is_regex: Whether pattern is regex
            case_sensitive: Case sensitivity
            max_results: Maximum results
            
        Returns:
            SearchResult
        """
        result = SearchResult(
            query=pattern,
            pattern_type="regex" if is_regex else "text",
        )
        
        files = self.find_files(file_pattern, path)
        
        for file_info in files:
            if result.total_matches >= max_results:
                break
            
            file_result = self.search_in_file(
                file_info.path, pattern, is_regex, case_sensitive
            )
            
            result.files_searched += 1
            
            if file_result.matches:
                result.files_matched += 1
                remaining = max_results - result.total_matches
                result.matches.extend(file_result.matches[:remaining])
                result.total_matches = len(result.matches)
        
        return result
    
    # ==========================================================================
    # Directory Operations
    # ==========================================================================
    
    def list_directory(
        self,
        path: str = "",
        recursive: bool = False,
    ) -> list[FileInfo]:
        """
        List directory contents.
        
        Args:
            path: Directory path
            recursive: Whether to recurse
            
        Returns:
            List of FileInfo
        """
        full_path = self._resolve_path(path)
        
        if not full_path.exists() or not full_path.is_dir():
            return []
        
        results: list[FileInfo] = []
        
        if recursive:
            for item in full_path.rglob("*"):
                if self._should_ignore(item):
                    continue
                results.append(self._get_file_info(item))
        else:
            for item in full_path.iterdir():
                if self._should_ignore(item):
                    continue
                results.append(self._get_file_info(item))
        
        return results
    
    def find_files(
        self,
        pattern: str,
        path: str = "",
    ) -> list[FileInfo]:
        """
        Find files matching a pattern.
        
        Args:
            pattern: Glob pattern (e.g., "*.py")
            path: Directory to search
            
        Returns:
            List of matching FileInfo
        """
        full_path = self._resolve_path(path)
        
        if not full_path.exists() or not full_path.is_dir():
            return []
        
        results: list[FileInfo] = []
        
        for item in full_path.rglob(pattern):
            if self._should_ignore(item):
                continue
            if item.is_file():
                results.append(self._get_file_info(item))
        
        return results
    
    def get_file_info(self, path: str) -> Optional[FileInfo]:
        """
        Get information about a file.
        
        Args:
            path: File path
            
        Returns:
            FileInfo or None
        """
        full_path = self._resolve_path(path)
        
        if not full_path.exists():
            return None
        
        return self._get_file_info(full_path)
    
    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        return self._resolve_path(path).exists()
    
    # ==========================================================================
    # Structure Analysis
    # ==========================================================================
    
    def get_directory_tree(
        self,
        path: str = "",
        max_depth: int = 3,
    ) -> dict[str, Any]:
        """
        Get directory tree structure.
        
        Args:
            path: Root path
            max_depth: Maximum depth
            
        Returns:
            Tree structure dict
        """
        full_path = self._resolve_path(path)
        
        if not full_path.exists():
            return {}
        
        return self._build_tree(full_path, max_depth, 0)
    
    def _build_tree(
        self,
        path: Path,
        max_depth: int,
        current_depth: int,
    ) -> dict[str, Any]:
        """Build tree structure recursively."""
        if current_depth >= max_depth:
            return {"_truncated": True}
        
        if path.is_file():
            return {
                "_type": "file",
                "_size": path.stat().st_size,
            }
        
        tree: dict[str, Any] = {"_type": "directory"}
        
        try:
            for item in sorted(path.iterdir()):
                if self._should_ignore(item):
                    continue
                tree[item.name] = self._build_tree(item, max_depth, current_depth + 1)
        except PermissionError:
            tree["_error"] = "permission_denied"
        
        return tree
    
    def get_project_summary(self, path: str = "") -> dict[str, Any]:
        """
        Get project structure summary.
        
        Args:
            path: Project root
            
        Returns:
            Summary dict
        """
        files = self.list_directory(path, recursive=True)
        
        # Count by extension
        by_extension: dict[str, int] = {}
        total_size = 0
        total_lines = 0
        
        for file_info in files:
            if not file_info.is_directory:
                ext = file_info.extension or "no_extension"
                by_extension[ext] = by_extension.get(ext, 0) + 1
                total_size += file_info.size_bytes
        
        return {
            "total_files": len([f for f in files if not f.is_directory]),
            "total_directories": len([f for f in files if f.is_directory]),
            "total_size_bytes": total_size,
            "files_by_extension": by_extension,
        }
    
    # ==========================================================================
    # Utility
    # ==========================================================================
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve a path relative to base."""
        if not path:
            return self._config.base_path
        return self._config.base_path / path
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        name = path.name
        for pattern in self._config.ignore_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False
    
    def _get_file_info(self, path: Path) -> FileInfo:
        """Get FileInfo for a path."""
        stat = path.stat()
        relative = str(path.relative_to(self._config.base_path))
        
        return FileInfo(
            path=relative,
            name=path.name,
            extension=path.suffix,
            size_bytes=stat.st_size if path.is_file() else 0,
            is_directory=path.is_dir(),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
        )
    
    def _update_cache(self, path: str, content: str, checksum: str) -> None:
        """Update the cache."""
        if len(self._cache) >= self._config.cache_max_size:
            # Remove oldest entry
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]
        
        self._cache[path] = (content, datetime.utcnow(), checksum)
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
    
    def set_base_path(self, path: Path) -> None:
        """Update base path."""
        self._config.base_path = path
        self.clear_cache()
