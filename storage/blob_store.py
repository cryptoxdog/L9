"""
L9 Storage - Blob Store
Version: 1.0.0

Minimal local blob store for heavy artifacts (images, audio, etc.).
Integrates with ArtifactPointer-style records via returned dicts.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Optional, BinaryIO, Dict


class BlobStore:
    """
    Local filesystem-backed blob store.

    In future this can be swapped for S3/GCS while keeping the same interface.
    """

    def __init__(self, root_dir: str = "data/blobs") -> None:
        self._root = Path(root_dir).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def _compute_checksum(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def save_bytes(
        self,
        data: bytes,
        mime_type: str,
        filename_hint: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Save raw bytes and return an ArtifactPointer-like dict.

        Returns:
            {
                "artifact_id": <sha256>,
                "mime_type": <mime>,
                "storage_path": <absolute path>,
                "checksum": <sha256>,
            }
        """
        checksum = self._compute_checksum(data)
        artifact_id = checksum
        ext = (filename_hint or "blob").split(".")[-1]
        rel_name = f"{artifact_id}.{ext}"
        path = self._root / rel_name

        with open(path, "wb") as f:
            f.write(data)

        return {
            "artifact_id": artifact_id,
            "mime_type": mime_type,
            "storage_path": str(path),
            "checksum": checksum,
        }

    def open(self, storage_path: str) -> BinaryIO:
        """Open a stored blob for reading."""
        return open(storage_path, "rb")

