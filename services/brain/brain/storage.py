"""Private storage for originals copied from the gallery (plan 05, K3).

Local directory for now; S3 on JODA replaces it in the deploy step with the
same interface. Files are content-addressed by sha256 and verified on write.
"""

import hashlib
from pathlib import Path

from brain.config import settings


class StorageError(Exception):
    pass


class LocalStorage:
    def __init__(self, root: Path | None = None):
        self.root = Path(root or settings.media_dir)

    def _path(self, sha256: str) -> Path:
        if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
            raise StorageError(f"invalid sha256: {sha256!r}")
        return self.root / "originals" / sha256[:2] / sha256

    def has(self, sha256: str) -> bool:
        return self._path(sha256).is_file()

    def put(self, sha256: str, data: bytes) -> None:
        if hashlib.sha256(data).hexdigest() != sha256:
            raise StorageError(f"checksum mismatch for {sha256}")
        path = self._path(sha256)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.replace(path)

    def get(self, sha256: str) -> bytes:
        path = self._path(sha256)
        if not path.is_file():
            raise StorageError(f"missing original {sha256}")
        return path.read_bytes()
