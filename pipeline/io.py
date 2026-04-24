"""
All filesystem I/O for the pipeline.
Owns: atomic writes, JSON load/save, cache read/write.
No business logic. No ML.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pipeline import config
from pipeline.models import CacheEntry, GraphData, PostCache, PostRecord, TagCache


def atomic_write_json(data: Any, target: Path, *, ensure_ascii: bool = False, indent: int = 2) -> None:
    """Write JSON to target atomically via temp file + os.replace()."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=ensure_ascii, indent=indent), encoding="utf-8")
    os.replace(tmp, target)


def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON from path. Returns default if file does not exist."""
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_post_cache(path: Path | None = None) -> PostCache:
    """Load .post_cache.json → {slug: {hash, embedding}}. Returns {} if missing."""
    return load_json(path or config.POST_CACHE, default={})


def save_post_cache(cache: PostCache, path: Path | None = None) -> None:
    """Atomically write .post_cache.json."""
    atomic_write_json(cache, path or config.POST_CACHE, indent=None)


def load_tag_cache(path: Path | None = None) -> TagCache:
    """Load .tag_cache.json → {tag: [float, ...]}. Returns {} if missing."""
    return load_json(path or config.TAG_CACHE, default={})


def save_tag_cache(cache: TagCache, path: Path | None = None) -> None:
    """Atomically write .tag_cache.json."""
    atomic_write_json(cache, path or config.TAG_CACHE, indent=None)


def load_posts_json(path: Path | None = None) -> list[dict]:
    """Load blog/posts.json. Returns [] if missing."""
    return load_json(path or config.POSTS_JSON, default=[])


def save_posts_json(
    posts: list[PostRecord],
    existing: list[dict],
    path: Path | None = None,
    force: bool = False,
) -> bool:
    """
    Merge scanned posts with existing posts.json entries (preserving manual entries).
    Strips internal '_' keys before writing.
    Writes atomically. Returns True if file content changed.

    If force=True, existing entries are discarded — only scanned posts are kept
    (deleted post folders are removed from posts.json).
    """
    target = path or config.POSTS_JSON
    existing_map: dict[str, dict] = (
        {} if force else {p["slug"]: p for p in existing}
    )

    merged = dict(existing_map)
    for p in posts:
        merged[p["slug"]] = {k: v for k, v in p.items() if not k.startswith("_")}

    result = sorted(merged.values(), key=lambda p: p["date"], reverse=True)

    new_text = json.dumps(result, ensure_ascii=False, indent=2)
    old_text = target.read_text(encoding="utf-8") if target.exists() else ""
    if new_text == old_text:
        return False

    atomic_write_json(result, target)
    return True


def save_graph_json(data: GraphData, path: Path | None = None) -> bool:
    """Atomically write graph.json. Returns True if content changed."""
    target = path or config.GRAPH_JSON
    new_text = json.dumps(data, ensure_ascii=False, indent=2)
    old_text = target.read_text(encoding="utf-8") if target.exists() else ""
    if new_text == old_text:
        return False
    atomic_write_json(data, target)
    return True


def save_tags_json(tags: list[str], path: Path | None = None) -> bool:
    """Atomically write sorted, deduplicated tags.json. Returns True if content changed."""
    target = path or config.TAGS_JSON
    sorted_tags = sorted(set(tags))
    new_text = json.dumps(sorted_tags, ensure_ascii=False, indent=2)
    old_text = target.read_text(encoding="utf-8") if target.exists() else ""
    if new_text == old_text:
        return False
    atomic_write_json(sorted_tags, target)
    return True


def load_vocabulary(path: Path | None = None) -> list[str]:
    """Load tag_vocabulary.json. Returns [] if missing."""
    return load_json(path or config.VOCAB_PATH, default=[])
