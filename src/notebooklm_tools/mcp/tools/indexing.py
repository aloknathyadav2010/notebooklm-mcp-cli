"""Local indexing tools for creating/rebuilding notebooks from directory content."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ._utils import get_client, logged_tool
from ...services import notebooks as notebooks_service, sources as sources_service, ServiceError
from ...services.local_indexing import (
    DEFAULT_MAX_FILES,
    get_index_entry,
    scan_local_files,
    select_files_for_upload,
    update_index_metadata,
)


def _upload_selected_files(
    notebook_id: str,
    *,
    selected_files: list,
    wait: bool,
    wait_timeout: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    uploaded_files: list[dict[str, Any]] = []
    failed_uploads: list[dict[str, Any]] = []

    for file_candidate in selected_files:
        try:
            result = sources_service.add_source(
                get_client(),
                notebook_id,
                "file",
                file_path=file_candidate.path,
                wait=wait,
                wait_timeout=wait_timeout,
            )
            uploaded_files.append({
                "path": file_candidate.path,
                "size_bytes": file_candidate.size_bytes,
                "media_type": file_candidate.media_type,
                "source_id": result["source_id"],
                "title": result["title"],
            })
        except Exception as e:
            failed_uploads.append({
                "path": file_candidate.path,
                "size_bytes": file_candidate.size_bytes,
                "media_type": file_candidate.media_type,
                "error": str(e),
            })

    return uploaded_files, failed_uploads


@logged_tool()
def notebook_index_local(
    root_dir: str = ".",
    notebook_title: str | None = None,
    metadata_file: str = ".notebooklm/indexed_notebooks.json",
    max_files: int = DEFAULT_MAX_FILES,
    wait: bool = True,
    wait_timeout: float = 180.0,
) -> dict[str, Any]:
    """Create notebook and index local text/pdf/video/image/word files recursively.

    If candidate files exceed max_files, selection prioritizes text/pdf/video,
    then image/word, with larger files first inside each priority band.
    """
    try:
        root = Path(root_dir).expanduser().resolve()
        files = scan_local_files(str(root))
        selected, skipped = select_files_for_upload(files, max_files=max_files)

        if not notebook_title:
            notebook_title = f"Local Index - {root.name} - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"

        notebook = notebooks_service.create_notebook(get_client(), notebook_title)
        notebook_id = notebook["notebook_id"]

        uploaded_files, failed_uploads = _upload_selected_files(
            notebook_id,
            selected_files=selected,
            wait=wait,
            wait_timeout=wait_timeout,
        )

        skipped_files = [
            {"path": f.path, "size_bytes": f.size_bytes, "media_type": f.media_type}
            for f in skipped
        ]

        metadata_entry = update_index_metadata(
            metadata_file,
            notebook_id=notebook_id,
            notebook_title=notebook["title"],
            root_dir=str(root),
            uploaded_files=uploaded_files,
            skipped_files=skipped_files,
            failed_uploads=failed_uploads,
            reindex=False,
        )

        return {
            "status": "success",
            "notebook": {
                "id": notebook_id,
                "title": notebook["title"],
                "url": notebook["url"],
            },
            "root_dir": str(root),
            "metadata_file": str(Path(metadata_file).expanduser().resolve()),
            "uploaded_count": len(uploaded_files),
            "skipped_count": len(skipped_files),
            "failed_count": len(failed_uploads),
            "uploaded_files": uploaded_files,
            "skipped_files": skipped_files,
            "failed_uploads": failed_uploads,
            "metadata": metadata_entry,
            "message": "Notebook created and local files indexed. You can now use existing query/studio tools.",
        }
    except ServiceError as e:
        return {"status": "error", "error": e.user_message}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@logged_tool()
def notebook_reindex_local(
    notebook_id: str | None = None,
    root_dir: str | None = None,
    metadata_file: str = ".notebooklm/indexed_notebooks.json",
    max_files: int = DEFAULT_MAX_FILES,
    wait: bool = True,
    wait_timeout: float = 180.0,
) -> dict[str, Any]:
    """Rebuild notebook indexing: remove existing sources and re-upload local files."""
    try:
        metadata_entry = get_index_entry(metadata_file, notebook_id)
        if not metadata_entry and (not notebook_id or not root_dir):
            return {
                "status": "error",
                "error": (
                    "No metadata found for notebook. Provide notebook_id + root_dir, "
                    "or run notebook_index_local first."
                ),
            }

        target_notebook_id = notebook_id or metadata_entry["notebook_id"]
        target_root_dir = root_dir or metadata_entry["root_dir"]

        notebook_detail = notebooks_service.get_notebook(get_client(), target_notebook_id)
        source_ids = [s["id"] for s in notebook_detail.get("sources", []) if s.get("id")]
        if source_ids:
            sources_service.delete_sources(get_client(), source_ids)

        files = scan_local_files(target_root_dir)
        selected, skipped = select_files_for_upload(files, max_files=max_files)
        uploaded_files, failed_uploads = _upload_selected_files(
            target_notebook_id,
            selected_files=selected,
            wait=wait,
            wait_timeout=wait_timeout,
        )

        skipped_files = [
            {"path": f.path, "size_bytes": f.size_bytes, "media_type": f.media_type}
            for f in skipped
        ]

        metadata = update_index_metadata(
            metadata_file,
            notebook_id=target_notebook_id,
            notebook_title=notebook_detail["title"],
            root_dir=target_root_dir,
            uploaded_files=uploaded_files,
            skipped_files=skipped_files,
            failed_uploads=failed_uploads,
            reindex=True,
        )

        return {
            "status": "success",
            "notebook_id": target_notebook_id,
            "root_dir": str(Path(target_root_dir).expanduser().resolve()),
            "metadata_file": str(Path(metadata_file).expanduser().resolve()),
            "deleted_source_count": len(source_ids),
            "uploaded_count": len(uploaded_files),
            "skipped_count": len(skipped_files),
            "failed_count": len(failed_uploads),
            "uploaded_files": uploaded_files,
            "skipped_files": skipped_files,
            "failed_uploads": failed_uploads,
            "metadata": metadata,
            "message": "Notebook reindex complete.",
        }
    except ServiceError as e:
        return {"status": "error", "error": e.user_message}
    except Exception as e:
        return {"status": "error", "error": str(e)}
