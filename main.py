#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
#   "nbformat",
#   "sentence-transformers",
#   "scikit-learn",
#   "numpy",
# ]
# ///
"""
Blog post update pipeline — single entry point.

Usage:
  uv run python main.py               # incremental update
  uv run python main.py --force       # ignore all caches, recompute embeddings + tags
  uv run python main.py --posts-only  # update posts.json only (skip ML stages)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import config, embedder, graph_builder, io, scanner, state, supernode_builder, tagger
from pipeline.models import RunState


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="posts.json + graph.json + tags.json 자동 업데이트"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="캐시 무시, 전체 임베딩 + 태그 centroid 재계산",
    )
    parser.add_argument(
        "--posts-only",
        action="store_true",
        help="posts.json만 업데이트 (ML 스테이지 스킵)",
    )
    return parser.parse_args()


def run_pipeline(force: bool = False, posts_only: bool = False) -> RunState:
    """
    Execute all pipeline stages in order. Returns RunState summarising what changed.

    Stage 1: Scan posts/ → List[PostRecord]
    Stage 2: Detect stale posts → RunState
    Stage 3 (skip if posts_only): Compute embeddings for stale posts
    Stage 4 (skip if posts_only): Build graph.json from embeddings + TF-IDF
    Stage 5 (skip if posts_only): Auto-tag tagless posts, save tags.json
    Stage 6: Save posts.json (with updated tags from stage 5)
    """
    # Stage 1
    print("포스트 스캔 중...")
    posts = scanner.scan_posts()
    print(f"  {len(posts)}개 포스트 발견")

    # Stage 2
    run_state = state.build_run_state(posts, force=force, posts_only=posts_only)

    if not posts_only:
        # Stage 3: embeddings
        existing_cache = io.load_post_cache()
        stale_posts = [p for p in posts if p["slug"] in run_state.stale_slugs]
        cache = embedder.compute_post_embeddings(stale_posts, existing_cache, force=force)

        # Stage 4: graph
        _, tfidf_per_post = graph_builder.build_graph(posts, cache)
        run_state.graph_json_changed = True

        # Stage 5: tags
        tagger.run_auto_tagging(posts, cache, tfidf_per_post, force=force)
        run_state.tags_json_changed = True

    # Stage 6: posts.json
    existing_posts = io.load_posts_json()
    run_state.posts_json_changed = io.save_posts_json(posts, existing_posts, force=force)
    print("posts.json 업데이트됨" if run_state.posts_json_changed else "posts.json 변경 없음")

    if not posts_only:
        # Re-build graph with normalised tags from stage 5
        cache = io.load_post_cache()
        graph_builder.build_graph(posts, cache)

        # Stage 8: supernodes
        print("슈퍼노드 군집화 중...")
        supernode_builder.build_supernodes(posts)

    return run_state


def _print_summary(run_state: RunState) -> None:
    print("\n=== 파이프라인 완료 ===")
    if run_state.stale_slugs:
        print(f"  임베딩 재계산: {sorted(run_state.stale_slugs)}")
    if run_state.unchanged_slugs:
        print(f"  캐시 유효: {len(run_state.unchanged_slugs)}개 포스트")
    changed = [
        name for name, flag in [
            ("posts.json", run_state.posts_json_changed),
            ("graph.json", run_state.graph_json_changed),
            ("tags.json", run_state.tags_json_changed),
        ] if flag
    ]
    if changed:
        print(f"  업데이트: {', '.join(changed)}")
    if run_state.errors:
        print(f"  오류: {run_state.errors}", file=sys.stderr)


def main() -> int:
    args = parse_args()
    try:
        run_state = run_pipeline(force=args.force, posts_only=args.posts_only)
        _print_summary(run_state)
        return 0
    except Exception as exc:
        print(f"파이프라인 실패: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
