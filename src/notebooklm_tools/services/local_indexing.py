"""Local filesystem indexing helpers for NotebookLM notebooks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from fnmatch import fnmatch
import json
import os
from pathlib import Path


DEFAULT_MAX_FILES = 50

# Common heavy/system directories to skip by default for beginner-friendly indexing.
DEFAULT_EXCLUDED_DIR_NAMES = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "dist", "build", "target",
    "__pycache__", ".mypy_cache", ".pytest_cache",
}

TEXT_EXTENSIONS = {
    ".txt", ".md", ".markdown", ".rst", ".csv", ".tsv", ".json", ".yaml", ".yml",
    ".xml", ".log", ".ini", ".toml", ".py", ".js", ".ts", ".tsx", ".jsx", ".java",
    ".go", ".rs", ".c", ".cpp", ".h", ".hpp", ".sh", ".sql",
}
PDF_EXTENSIONS = {".pdf"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff"}
WORD_EXTENSIONS = {".doc", ".docx", ".rtf", ".odt"}


@dataclass(frozen=True)
class FileCandidate:
    """A local file candidate for indexing."""

    path: str
    size_bytes: int
    media_type: str
    priority: int


def classify_file(path: Path) -> tuple[str, int] | None:
    """Classify a file by extension and assign selection priority."""
    ext = path.suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return "text", 3
    if ext in PDF_EXTENSIONS:
        return "pdf", 3
    if ext in VIDEO_EXTENSIONS:
        return "video", 3
    if ext in AUDIO_EXTENSIONS:
        return "audio", 3
    if ext in IMAGE_EXTENSIONS:
        return "image", 2
    if ext in WORD_EXTENSIONS:
        return "word", 2
    return None


def _read_gitignore_patterns(root: Path) -> list[str]:
    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists() or not gitignore_path.is_file():
        return []

    patterns: list[str] = []
    for raw in gitignore_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("!"):
            # Negation support can be added later; for MVP keep behavior predictable.
            continue
        patterns.append(line)
    return patterns


def _path_is_ignored(rel_path: str, patterns: list[str]) -> bool:
    rel_norm = rel_path.replace("\\", "/")
    for pattern in patterns:
        p = pattern.replace("\\", "/")
        # Directory pattern in .gitignore (e.g., build/)
        if p.endswith("/"):
            p_dir = p.rstrip("/")
            if rel_norm == p_dir or rel_norm.startswith(p_dir + "/"):
                return True
        # Rooted pattern
        if p.startswith("/"):
            p = p[1:]
            if fnmatch(rel_norm, p):
                return True
            continue
        # General glob
        if fnmatch(rel_norm, p) or fnmatch(Path(rel_norm).name, p):
            return True
    return False


def scan_local_files(root_dir: str) -> list[FileCandidate]:
    """Recursively scan and classify supported files under root_dir.

    Ignores files/folders from .gitignore and common heavy/system directories.
    """
def scan_local_files(root_dir: str) -> list[FileCandidate]:
    """Recursively scan and classify supported files under root_dir."""
    root = Path(root_dir).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Directory does not exist or is not a directory: {root}")

    gitignore_patterns = _read_gitignore_patterns(root)

    candidates: list[FileCandidate] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dir_rel = str(Path(dirpath).resolve().relative_to(root)).replace("\\", "/")

        pruned_dirs = []
        for d in dirnames:
            if d in DEFAULT_EXCLUDED_DIR_NAMES:
                continue
            rel = d if dir_rel == "." else f"{dir_rel}/{d}"
            if _path_is_ignored(rel, gitignore_patterns):
                continue
            pruned_dirs.append(d)
        dirnames[:] = pruned_dirs

        for filename in filenames:
            full_path = Path(dirpath) / filename
            if full_path.is_symlink() or not full_path.is_file():
                continue

            rel = str(full_path.resolve().relative_to(root)).replace("\\", "/")
            if _path_is_ignored(rel, gitignore_patterns):
                continue

            classified = classify_file(full_path)
            if not classified:
                continue
            media_type, priority = classified
            try:
                size = full_path.stat().st_size
            except OSError:
                continue
            candidates.append(FileCandidate(path=str(full_path), size_bytes=size, media_type=media_type, priority=priority))
    candidates: list[FileCandidate] = []
    for p in root.rglob("*"):
        if not p.is_file() or p.is_symlink():
            continue
        classified = classify_file(p)
        if not classified:
            continue
        media_type, priority = classified
        try:
            size = p.stat().st_size
        except OSError:
            continue
        candidates.append(FileCandidate(path=str(p), size_bytes=size, media_type=media_type, priority=priority))

    return candidates


def select_files_for_upload(candidates: list[FileCandidate], max_files: int = DEFAULT_MAX_FILES) -> tuple[list[FileCandidate], list[FileCandidate]]:
    """Select highest priority/largest files within max_files cap."""
    if max_files <= 0:
        return [], sorted(candidates, key=lambda c: (c.priority, c.size_bytes), reverse=True)

    ranked = sorted(candidates, key=lambda c: (c.priority, c.size_bytes), reverse=True)
    selected = ranked[:max_files]
    skipped = ranked[max_files:]
    return selected, skipped


def _load_metadata_file(metadata_file: Path) -> dict:
    if not metadata_file.exists():
        return {"entries": [], "last_notebook_id": None}
    try:
        return json.loads(metadata_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"entries": [], "last_notebook_id": None}


def update_index_metadata(
    metadata_file: str,
    *,
    notebook_id: str,
    notebook_title: str,
    root_dir: str,
    uploaded_files: list[dict],
    skipped_files: list[dict],
    failed_uploads: list[dict],
    reindex: bool,
) -> dict:
    """Write/update JSON metadata for local indexing runs."""
    target = Path(metadata_file).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    payload = _load_metadata_file(target)
    entries = payload.get("entries") or []
    run_at = datetime.now(timezone.utc).isoformat()

    entry = {
        "notebook_id": notebook_id,
        "notebook_title": notebook_title,
        "root_dir": str(Path(root_dir).expanduser().resolve()),
        "last_updated": run_at,
        "uploaded_files": uploaded_files,
        "skipped_files": skipped_files,
        "failed_uploads": failed_uploads,
        "upload_count": len(uploaded_files),
        "skipped_count": len(skipped_files),
        "failed_count": len(failed_uploads),
        "last_operation": "reindex" if reindex else "create_and_index",
    }

    replaced = False
    for i, existing in enumerate(entries):
        if existing.get("notebook_id") == notebook_id:
            entries[i] = entry
            replaced = True
            break

    if not replaced:
        entries.append(entry)

    payload["entries"] = entries
    payload["last_notebook_id"] = notebook_id
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return entry


def get_index_entry(metadata_file: str, notebook_id: str | None = None) -> dict | None:
    """Get notebook metadata entry by id or last notebook."""
    target = Path(metadata_file).expanduser().resolve()
    payload = _load_metadata_file(target)
    entries = payload.get("entries") or []
    wanted = notebook_id or payload.get("last_notebook_id")
    if not wanted:
        return None

    for entry in entries:
        if entry.get("notebook_id") == wanted:
            return entry
    return None
