import os
from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import StorageError
from app.core.logging import get_logger

logger = get_logger(__name__)


async def save_artifact(
    content: str | bytes,
    *,
    path: str,
) -> str:
    """Save raw content to storage. Returns the storage path."""
    settings = get_settings()

    if settings.storage_backend == "local":
        return await _save_local(content, path=path)
    elif settings.storage_backend == "s3":
        return await _save_s3(content, path=path)
    else:
        raise StorageError(f"Unknown storage backend: {settings.storage_backend}")


async def load_artifact(path: str) -> str | bytes:
    """Load raw content from storage."""
    settings = get_settings()

    if settings.storage_backend == "local":
        return await _load_local(path)
    elif settings.storage_backend == "s3":
        return await _load_s3(path)
    else:
        raise StorageError(f"Unknown storage backend: {settings.storage_backend}")


async def _save_local(content: str | bytes, *, path: str) -> str:
    settings = get_settings()
    full_path = Path(settings.local_storage_path) / path

    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(full_path, mode) as f:
            f.write(content)
        logger.info("storage_save_local", path=str(full_path))
        return str(full_path)
    except OSError as exc:
        raise StorageError(f"Failed to save to {full_path}") from exc


async def _load_local(path: str) -> str:
    settings = get_settings()
    full_path = Path(settings.local_storage_path) / path

    if not os.path.exists(full_path):
        full_path = Path(path)

    try:
        with open(full_path) as f:
            return f.read()
    except OSError as exc:
        raise StorageError(f"Failed to load from {full_path}") from exc


async def _save_s3(content: str | bytes, *, path: str) -> str:
    raise StorageError("S3 storage not yet implemented")


async def _load_s3(path: str) -> str | bytes:
    raise StorageError("S3 storage not yet implemented")
