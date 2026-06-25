from __future__ import annotations

from pathlib import Path


def _load_impl() -> None:
    source_path = Path(__file__).with_name("video_export_source.txt")
    source = source_path.read_text(encoding="utf-8")
    exec(compile(source, str(source_path), "exec"), globals())


_load_impl()
