from pathlib import Path

from notebooklm_tools.services.local_indexing import (
    FileCandidate,
    classify_file,
    get_index_entry,
    scan_local_files,
    select_files_for_upload,
    update_index_metadata,
)


def test_classify_file_supported_types():
    assert classify_file(Path("a.md")) == ("text", 3)
    assert classify_file(Path("a.pdf")) == ("pdf", 3)
    assert classify_file(Path("a.mp4")) == ("video", 3)
    assert classify_file(Path("a.mp3")) == ("audio", 3)
    assert classify_file(Path("a.png")) == ("image", 2)
    assert classify_file(Path("a.docx")) == ("word", 2)
    assert classify_file(Path("a.bin")) is None


def test_select_files_prefers_priority_then_size():
    candidates = [
        FileCandidate(path="a.png", size_bytes=1000, media_type="image", priority=2),
        FileCandidate(path="b.mp4", size_bytes=100, media_type="video", priority=3),
        FileCandidate(path="c.txt", size_bytes=50, media_type="text", priority=3),
        FileCandidate(path="d.pdf", size_bytes=200, media_type="pdf", priority=3),
    ]

    selected, skipped = select_files_for_upload(candidates, max_files=2)

    assert [f.path for f in selected] == ["d.pdf", "b.mp4"]
    assert [f.path for f in skipped] == ["c.txt", "a.png"]


def test_scan_local_files_respects_gitignore_and_default_excludes(tmp_path):
    (tmp_path / ".gitignore").write_text("ignored.md\nbuild/\n", encoding="utf-8")
    (tmp_path / "a.md").write_text("ok", encoding="utf-8")
    (tmp_path / "ignored.md").write_text("no", encoding="utf-8")

    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "inside.pdf").write_bytes(b"x")

    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "mod.txt").write_text("no", encoding="utf-8")

    files = scan_local_files(str(tmp_path))
    names = {Path(f.path).name for f in files}

    assert "a.md" in names
    assert "ignored.md" not in names
    assert "inside.pdf" not in names
    assert "mod.txt" not in names


def test_scan_local_files_and_metadata_roundtrip(tmp_path):
    (tmp_path / "a.md").write_text("hello", encoding="utf-8")
    (tmp_path / "b.pdf").write_bytes(b"pdf")
    (tmp_path / "skip.exe").write_bytes(b"x")

    files = scan_local_files(str(tmp_path))
    assert {Path(f.path).name for f in files} == {"a.md", "b.pdf"}

    metadata_file = tmp_path / ".notebooklm" / "indexed_notebooks.json"
    entry = update_index_metadata(
        str(metadata_file),
        notebook_id="nb1",
        notebook_title="Notebook",
        root_dir=str(tmp_path),
        uploaded_files=[{"path": "a.md"}],
        skipped_files=[{"path": "b.pdf"}],
        failed_uploads=[],
        reindex=False,
    )

    assert entry["notebook_id"] == "nb1"
    loaded = get_index_entry(str(metadata_file), "nb1")
    assert loaded is not None
    assert loaded["upload_count"] == 1
