# 자동 태그 시스템 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 포스트 본문을 분석하여 자동으로 태그를 추천/생성하는 시스템. API 없이 로컬 임베딩만 사용.

**Architecture:** 포스트 임베딩(build_graph.py 캐시 재사용)과 태그 임베딩(해당 태그를 가진 포스트들의 centroid)을 cosine similarity로 비교하여 태그를 매칭한다. 매칭 실패 시 TF-IDF 키워드에서 새 태그를 생성한다.

**Tech Stack:** sentence-transformers (기존), scikit-learn (기존), numpy (기존) — 추가 의존성 없음

---

## 현재 상태 분석

### 문제점
1. "DL", "Deep-Learning", "deep-learning" 등 중복 태그가 별도로 존재
2. 기존 auto_tag.py는 유사 포스트 투표 방식 — 기존 나쁜 태그를 그대로 전파
3. 태그 임베딩이 없어 의미 기반 매칭 불가
4. frontmatter에서 태그를 제거하면 태그를 새로 생성하는 로직 없음

### 재사용할 것
- `build_graph.py`: `compute_embeddings()`, `get_post_text()`, `extract_tfidf_keywords()`, 포스트 임베딩 캐시(`.post_cache.json`)
- `posts_list_update.py`: `scan_posts()`, `parse_frontmatter()`
- 의존성: sentence-transformers, scikit-learn, numpy, pyyaml 전부 기존 그대로

### 현재 깨진 상태
- `post_update.py`가 기존 `auto_tag.py`의 `init_tags`, `suggest_tags` 등을 import하는데, 이 함수들의 시그니처가 변경될 예정. Task 6에서 `post_update.py`를 전면 교체해야 함.

### 삭제할 것
- `blog/tags_registry.json` (있다면)
- `scripts/extract_tags.py` — auto_tag.py로 대체

## 파일 구조

```
blog/
  tags.json              # [사용자 편의] 정규화된 태그 이름 배열 (자동생성)
  .tag_cache.json         # [임베딩 캐시] {tag: embedding_vector} (자동생성, gitignore)

scripts/
  auto_tag.py             # 태그 추천 + 생성 + 임베딩 관리 (전면 재작성)
  post_update.py          # 파이프라인 통합 (수정)
  build_graph.py          # 변경 없음
  posts_list_update.py    # 변경 없음
```

## 핵심 로직 설계

### 태그 임베딩 계산
각 태그의 임베딩 = 해당 태그를 가진 포스트 임베딩들의 centroid (평균 벡터)

```
tag "deep-learning" embedding = mean(
    embedding("인공신경망1"),
    embedding("딥러닝과_신경망")
)
```

### 태그 추천 (기존 태그에서 매칭)
1. 대상 포스트 임베딩 계산 (캐시 재사용)
2. 모든 태그 임베딩과 cosine similarity 계산
3. threshold(0.4) 이상 + 상위 MAX_TAGS(5)개 선택

### 태그 생성 (새 태그 필요 시)
매칭 태그가 MIN_TAGS(2)개 미만일 때:
1. `extract_tfidf_keywords()`로 포스트의 상위 키워드 추출
2. 키워드를 정규화 (`normalize_tag()`)
3. 기존 태그와 중복 확인 (임베딩 유사도 0.8 이상이면 기존 태그 사용)
4. 중복 아니면 새 태그로 등록

### 부트스트랩 (태그가 하나도 없을 때)
기존 태그가 0개인 경우:
1. 모든 포스트에서 TF-IDF 키워드 추출
2. 키워드를 정규화하여 초기 태그 목록 생성
3. 태그 임베딩 계산 후 중복 태그 병합 (유사도 0.8 이상)

### 파이프라인 순서
```
scan_posts → update_graph (임베딩 캐시 생성) → init_tags (태그 임베딩) → assign_tags (빈 포스트) → normalize → posts.json → update_graph (태그 반영)
```
`update_graph()`를 먼저 한 번 호출하여 `.post_cache.json`을 채운다. `get_post_embeddings()`는 이 캐시를 읽기만 한다.

---

## Task 1: auto_tag.py 전면 재작성 — 기본 구조 + 태그 I/O

**Files:**
- Create: `scripts/auto_tag.py` (기존 파일 전면 교체)
- Test: `scripts/test_auto_tag.py`

- [ ] **Step 1: 테스트 작성 — normalize_tag + load/save**

```python
# scripts/test_auto_tag.py
import json
import tempfile
from pathlib import Path

def test_normalize_tag():
    from auto_tag import normalize_tag
    assert normalize_tag("Deep-Learning") == "deep-learning"
    assert normalize_tag("DL") == "dl"
    assert normalize_tag("computer vision") == "computer-vision"
    assert normalize_tag("  PyTorch ") == "pytorch"
    assert normalize_tag("deep_learning") == "deep-learning"

def test_save_load_tags(tmp_path):
    from auto_tag import save_tags, load_tags
    path = tmp_path / "tags.json"
    save_tags(["python", "deep-learning", "docker"], path)
    assert load_tags(path) == ["deep-learning", "docker", "python"]  # save_tags가 정렬

def test_save_load_tag_cache(tmp_path):
    from auto_tag import save_tag_cache, load_tag_cache
    path = tmp_path / ".tag_cache.json"
    data = {"python": [0.1, 0.2], "docker": [0.3, 0.4]}
    save_tag_cache(data, path)
    loaded = load_tag_cache(path)
    assert list(loaded.keys()) == ["python", "docker"]
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

Run: `cd /home/ahris/ahrism-pages/scripts && uv run pytest test_auto_tag.py -v`
Expected: FAIL (auto_tag 모듈의 함수 시그니처가 다름)

- [ ] **Step 3: auto_tag.py 기본 구조 구현**

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
#   "sentence-transformers",
#   "scikit-learn",
#   "numpy",
# ]
# ///
"""
자동 태그 시스템.

- 포스트 임베딩 vs 태그 임베딩 비교로 태그 추천
- 매칭 부족 시 TF-IDF 키워드에서 새 태그 생성
- API 없이 로컬 임베딩만 사용

Usage:
  uv run python auto_tag.py init                # tags.json + 태그 임베딩 초기화
  uv run python auto_tag.py suggest <slug>       # 특정 포스트 태그 추천
  uv run python auto_tag.py suggest --all        # 전체 포스트 태그 추천
"""

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TAGS_PATH = ROOT / "blog" / "tags.json"
TAG_CACHE_PATH = ROOT / "blog" / ".tag_cache.json"

MATCH_THRESHOLD = 0.4
NEW_TAG_DEDUP_THRESHOLD = 0.8
MAX_TAGS = 5
MIN_TAGS = 2


def normalize_tag(tag: str) -> str:
    return tag.strip().lower().replace(" ", "-").replace("_", "-")


def load_tags(path: Path = TAGS_PATH) -> list[str]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def save_tags(tags: list[str], path: Path = TAGS_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(sorted(set(tags)), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_tag_cache(path: Path = TAG_CACHE_PATH) -> dict[str, list[float]]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_tag_cache(cache: dict[str, list[float]], path: Path = TAG_CACHE_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(cache, ensure_ascii=False),
        encoding="utf-8",
    )
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

Run: `cd /home/ahris/ahrism-pages/scripts && uv run pytest test_auto_tag.py -v`
Expected: 3 passed

- [ ] **Step 5: 커밋**

```bash
git add scripts/auto_tag.py scripts/test_auto_tag.py
git commit -m "refactor: auto_tag.py 기본 구조 재작성 — normalize, tags I/O, tag cache I/O"
```

---

## Task 2: 태그 임베딩 계산 (update_tag_cache)

**Files:**
- Modify: `scripts/auto_tag.py`
- Modify: `scripts/test_auto_tag.py`

- [ ] **Step 1: 테스트 작성**

```python
def test_compute_tag_embeddings():
    """태그 임베딩 = 해당 태그를 가진 포스트 임베딩의 centroid."""
    from auto_tag import compute_tag_embeddings
    import numpy as np

    post_embeddings = {
        "post-a": np.array([1.0, 0.0, 0.0]),
        "post-b": np.array([0.0, 1.0, 0.0]),
        "post-c": np.array([1.0, 1.0, 0.0]),
    }
    posts = [
        {"slug": "post-a", "tags": ["python", "ml"]},
        {"slug": "post-b", "tags": ["python", "docker"]},
        {"slug": "post-c", "tags": ["ml"]},
    ]
    result = compute_tag_embeddings(posts, post_embeddings)

    # python = mean(post-a, post-b) = [0.5, 0.5, 0.0]
    np.testing.assert_array_almost_equal(result["python"], [0.5, 0.5, 0.0])
    # ml = mean(post-a, post-c) = [1.0, 0.5, 0.0]
    np.testing.assert_array_almost_equal(result["ml"], [1.0, 0.5, 0.0])
    # docker = mean(post-b) = [0.0, 1.0, 0.0]
    np.testing.assert_array_almost_equal(result["docker"], [0.0, 1.0, 0.0])
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd /home/ahris/ahrism-pages/scripts && uv run pytest test_auto_tag.py::test_compute_tag_embeddings -v`
Expected: FAIL

- [ ] **Step 3: compute_tag_embeddings 구현**

`auto_tag.py`에 추가:

```python
def compute_tag_embeddings(
    posts: list[dict],
    post_embeddings: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """각 태그의 임베딩을 해당 태그를 가진 포스트 임베딩의 centroid로 계산."""
    tag_vectors: dict[str, list[np.ndarray]] = {}
    for post in posts:
        slug = post["slug"]
        if slug not in post_embeddings:
            continue
        emb = post_embeddings[slug]
        for tag in post.get("tags", []):
            canonical = normalize_tag(tag)
            tag_vectors.setdefault(canonical, []).append(emb)

    return {
        tag: np.mean(vectors, axis=0)
        for tag, vectors in tag_vectors.items()
    }
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd /home/ahris/ahrism-pages/scripts && uv run pytest test_auto_tag.py -v`
Expected: all passed

- [ ] **Step 5: 커밋**

```bash
git add scripts/auto_tag.py scripts/test_auto_tag.py
git commit -m "feat: compute_tag_embeddings — 태그별 centroid 임베딩 계산"
```

---

## Task 3: 태그 추천 (recommend_tags)

**Files:**
- Modify: `scripts/auto_tag.py`
- Modify: `scripts/test_auto_tag.py`

- [ ] **Step 1: 테스트 작성**

```python
def test_recommend_tags():
    """포스트 임베딩과 태그 임베딩의 cosine similarity로 추천."""
    from auto_tag import recommend_tags
    import numpy as np

    post_emb = np.array([1.0, 0.0, 0.0])
    tag_cache = {
        "ml": np.array([0.9, 0.1, 0.0]),         # 높은 유사도
        "docker": np.array([0.0, 0.0, 1.0]),      # 낮은 유사도
        "python": np.array([0.7, 0.3, 0.0]),      # 중간 유사도
    }
    result = recommend_tags(post_emb, tag_cache, threshold=0.4, max_tags=5)
    tags = [t for t, _ in result]
    assert "ml" in tags
    assert "python" in tags
    assert "docker" not in tags  # 유사도 낮아서 제외

def test_recommend_tags_empty():
    from auto_tag import recommend_tags
    import numpy as np
    result = recommend_tags(np.array([1.0, 0.0]), {}, threshold=0.4, max_tags=5)
    assert result == []
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd /home/ahris/ahrism-pages/scripts && uv run pytest test_auto_tag.py::test_recommend_tags -v`

- [ ] **Step 3: recommend_tags 구현**

```python
from sklearn.metrics.pairwise import cosine_similarity

def recommend_tags(
    post_emb: np.ndarray,
    tag_cache: dict[str, np.ndarray],
    threshold: float = MATCH_THRESHOLD,
    max_tags: int = MAX_TAGS,
) -> list[tuple[str, float]]:
    """포스트 임베딩과 태그 임베딩의 cosine similarity로 태그 추천.

    Returns: [(tag, similarity), ...] 유사도 내림차순
    """
    if not tag_cache:
        return []

    tag_names = list(tag_cache.keys())
    tag_embs = np.array([tag_cache[t] for t in tag_names])
    sims = cosine_similarity([post_emb], tag_embs)[0]

    ranked = sorted(zip(tag_names, sims), key=lambda x: x[1], reverse=True)
    return [(t, float(s)) for t, s in ranked if s >= threshold][:max_tags]
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd /home/ahris/ahrism-pages/scripts && uv run pytest test_auto_tag.py -v`

- [ ] **Step 5: 커밋**

```bash
git add scripts/auto_tag.py scripts/test_auto_tag.py
git commit -m "feat: recommend_tags — cosine similarity 기반 태그 추천"
```

---

## Task 4: 태그 생성 (generate_new_tags)

**Files:**
- Modify: `scripts/auto_tag.py`
- Modify: `scripts/test_auto_tag.py`

- [ ] **Step 1: 테스트 작성**

```python
def test_generate_new_tags():
    """TF-IDF 키워드에서 새 태그 후보 생성, 기존 태그와 중복 제거."""
    from auto_tag import generate_new_tags
    import numpy as np

    # 기존 태그가 없으면 키워드가 그대로 태그가 됨
    keywords = ["신경망", "pytorch", "역전파"]
    existing_cache = {}
    result = generate_new_tags(keywords, existing_cache, max_new=2)
    assert len(result) <= 2
    assert all(isinstance(t, str) for t in result)

def test_generate_new_tags_dedup():
    """기존 태그와 이름이 겹치면 제외."""
    from auto_tag import generate_new_tags
    import numpy as np

    keywords = ["python", "새키워드"]
    existing_cache = {"python": np.array([0.1, 0.2])}
    result = generate_new_tags(keywords, existing_cache, max_new=3)
    assert "python" not in result
```

- [ ] **Step 2: 테스트 실패 확인**

- [ ] **Step 3: generate_new_tags 구현**

```python
def generate_new_tags(
    tfidf_keywords: list[str],
    existing_cache: dict[str, np.ndarray],
    max_new: int = 3,
) -> list[str]:
    """TF-IDF 키워드에서 새 태그 후보 생성.

    기존 태그와 이름이 같으면 제외.
    """
    existing_names = set(existing_cache.keys())
    candidates = []
    for kw in tfidf_keywords:
        normalized = normalize_tag(kw)
        if normalized and normalized not in existing_names and len(normalized) >= 2:
            candidates.append(normalized)
        if len(candidates) >= max_new:
            break
    return candidates
```

- [ ] **Step 4: 테스트 통과 확인**

- [ ] **Step 5: 커밋**

```bash
git add scripts/auto_tag.py scripts/test_auto_tag.py
git commit -m "feat: generate_new_tags — TF-IDF 키워드에서 새 태그 생성"
```

---

## Task 5: 통합 함수 (assign_tags) + init

**Files:**
- Modify: `scripts/auto_tag.py`
- Modify: `scripts/test_auto_tag.py`

- [ ] **Step 1: 테스트 작성**

```python
def test_assign_tags_with_existing():
    """기존 태그가 있으면 추천으로 채움."""
    from auto_tag import assign_tags
    import numpy as np

    post = {"slug": "test", "tags": [], "_body": "딥러닝 신경망 학습"}
    post_emb = np.array([1.0, 0.0])
    tag_cache = {"deep-learning": np.array([0.9, 0.1])}

    result = assign_tags(post_emb, tag_cache, tfidf_keywords=[], min_tags=1)
    assert "deep-learning" in result

def test_assign_tags_fallback_to_generate():
    """추천이 부족하면 TF-IDF에서 새 태그 생성."""
    from auto_tag import assign_tags
    import numpy as np

    post_emb = np.array([1.0, 0.0])
    tag_cache = {"docker": np.array([0.0, 1.0])}  # 유사도 낮음

    result = assign_tags(post_emb, tag_cache, tfidf_keywords=["pytorch", "신경망"], min_tags=2)
    assert len(result) >= 2
```

- [ ] **Step 2: 테스트 실패 확인**

- [ ] **Step 3: assign_tags + init_tags 구현**

```python
def assign_tags(
    post_emb: np.ndarray,
    tag_cache: dict[str, np.ndarray],
    tfidf_keywords: list[str],
    threshold: float = MATCH_THRESHOLD,
    max_tags: int = MAX_TAGS,
    min_tags: int = MIN_TAGS,
) -> list[str]:
    """포스트에 태그 할당: 추천 우선, 부족하면 생성."""
    recommended = recommend_tags(post_emb, tag_cache, threshold, max_tags)
    tags = [t for t, _ in recommended]

    if len(tags) < min_tags:
        new_tags = generate_new_tags(tfidf_keywords, tag_cache, max_new=min_tags - len(tags))
        tags.extend(new_tags)

    return tags[:max_tags]


def get_post_embeddings(posts: list[dict]) -> dict[str, np.ndarray]:
    """build_graph.py의 .post_cache.json에서 포스트 임베딩 로드.

    주의: update_graph()가 이미 실행되어 캐시가 최신 상태여야 한다.
    캐시에 없는 포스트만 추가 계산한다.
    """
    from build_graph import load_cache

    cache = load_cache()
    result = {}
    for p in posts:
        if p["slug"] in cache:
            result[p["slug"]] = np.array(cache[p["slug"]]["embedding"])
    return result


def init_tags(posts: list[dict]) -> tuple[list[str], dict[str, np.ndarray]]:
    """기존 포스트에서 태그 목록 + 태그 임베딩 초기화."""
    post_embs = get_post_embeddings(posts)
    tag_embs = compute_tag_embeddings(posts, post_embs)

    tags = sorted(tag_embs.keys())
    save_tags(tags)
    save_tag_cache({t: e.tolist() for t, e in tag_embs.items()})

    print(f"tags.json: {len(tags)}개 태그")
    print(f".tag_cache.json: 임베딩 저장 완료")
    return tags, tag_embs
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd /home/ahris/ahrism-pages/scripts && uv run pytest test_auto_tag.py -v`

- [ ] **Step 5: 커밋**

```bash
git add scripts/auto_tag.py scripts/test_auto_tag.py
git commit -m "feat: assign_tags + init_tags — 태그 할당 통합 로직"
```

---

## Task 6: CLI + post_update.py 통합

**Files:**
- Modify: `scripts/auto_tag.py` (CLI 부분)
- Modify: `scripts/post_update.py`
- Delete: `scripts/extract_tags.py`
- Delete: `blog/tags_registry.json` (있다면)

- [ ] **Step 1: auto_tag.py CLI 작성**

```python
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="자동 태그 시스템")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="기존 포스트에서 tags.json + 태그 임베딩 초기화")

    sp = sub.add_parser("suggest", help="태그 추천")
    sp.add_argument("slug", nargs="?", help="포스트 slug")
    sp.add_argument("--all", action="store_true", help="전체 포스트")

    args = parser.parse_args()
    from posts_list_update import scan_posts
    from build_graph import extract_tfidf_keywords, get_post_text

    if args.command == "init":
        posts = scan_posts()
        print(f"{len(posts)}개 포스트 스캔")
        tags, _ = init_tags(posts)
        print(f"태그: {tags}")

    elif args.command == "suggest":
        posts = scan_posts()
        tag_cache_raw = load_tag_cache()
        if not tag_cache_raw:
            print("태그 캐시가 없습니다. 먼저 'init'을 실행하세요.", file=sys.stderr)
            sys.exit(1)

        tag_cache = {t: np.array(e) for t, e in tag_cache_raw.items()}
        post_embs = get_post_embeddings(posts)

        targets = posts if args.all else [p for p in posts if p["slug"] == args.slug]
        if not targets:
            print(f"'{args.slug}' 포스트를 찾을 수 없습니다.", file=sys.stderr)
            sys.exit(1)

        # TF-IDF는 전체 포스트 컨텍스트로 계산 (단일 문서 IDF 퇴화 방지)
        all_texts = [get_post_text(p) for p in posts]
        all_kw_lists = extract_tfidf_keywords(all_texts, top_n=10)
        slug_to_idx = {p["slug"]: i for i, p in enumerate(posts)}

        for post in targets:
            idx = slug_to_idx[post["slug"]]
            kw_list = list(all_kw_lists[idx].keys()) if idx < len(all_kw_lists) else []

            tags = assign_tags(post_embs[post["slug"]], tag_cache, kw_list)
            current = [normalize_tag(t) for t in post.get("tags", [])]
            print(f"[{post['slug']}] 현재: {current} → 추천: {tags}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: post_update.py 수정**

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
#   "sentence-transformers",
#   "scikit-learn",
#   "numpy",
# ]
# ///
"""
posts.json + graph.json + tags.json 한 번에 업데이트.

Usage:
  uv run python post_update.py               # 증분 업데이트
  uv run python post_update.py --force       # 캐시 무시, 전체 임베딩 재계산
  uv run python post_update.py --posts-only  # posts.json만 업데이트 (그래프 스킵)
"""

import argparse

from posts_list_update import scan_posts, update_posts_json
from build_graph import update_graph, extract_tfidf_keywords, get_post_text
from auto_tag import (
    init_tags, assign_tags, get_post_embeddings,
    load_tag_cache, normalize_tag, save_tags,
)
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="posts.json + graph.json + tags 자동 업데이트")
    parser.add_argument("--force", action="store_true", help="캐시 무시, 전체 임베딩 재계산")
    parser.add_argument("--posts-only", action="store_true", help="posts.json만 업데이트 (그래프 스킵)")
    args = parser.parse_args()

    print("포스트 스캔 중...")
    posts = scan_posts()
    print(f"  {len(posts)}개 포스트 발견")

    if not args.posts_only:
        # 1) 임베딩 캐시 생성 (update_graph가 .post_cache.json을 채움)
        update_graph(posts, force=args.force)

        # 2) 태그가 있는 포스트로 태그 임베딩 초기화
        tagged_posts = [p for p in posts if p.get("tags")]
        if tagged_posts:
            known_tags, tag_embs = init_tags(tagged_posts)
        else:
            known_tags, tag_embs = [], {}

        # 3) 태그 없는 포스트에 자동 할당
        tagless = [p for p in posts if not p.get("tags")]
        if tagless:
            post_embs = get_post_embeddings(posts)
            tag_cache = {t: np.array(e) for t, e in load_tag_cache().items()}
            # TF-IDF는 전체 포스트 컨텍스트로 계산 (단일 문서 IDF 퇴화 방지)
            all_texts = [get_post_text(p) for p in posts]
            all_kw_lists = extract_tfidf_keywords(all_texts, top_n=10)
            # tagless 포스트의 인덱스 매핑
            tagless_indices = [i for i, p in enumerate(posts) if not p.get("tags")]

            new_tags_added = []
            for j, post in enumerate(tagless):
                kw = list(all_kw_lists[tagless_indices[j]].keys()) if tagless_indices[j] < len(all_kw_lists) else []
                post["tags"] = assign_tags(post_embs[post["slug"]], tag_cache, kw)
                new_tags_added.extend(post["tags"])
                print(f"  태그 할당: [{post['slug']}] → {post['tags']}")

            # 새로 생성된 태그를 tags.json에 추가
            if new_tags_added:
                all_tags = sorted(set(known_tags + new_tags_added))
                save_tags(all_tags)

        # 4) 모든 태그 정규화
        for post in posts:
            post["tags"] = [normalize_tag(t) for t in post.get("tags", [])]

    changed = update_posts_json(posts)
    print("posts.json 업데이트됨" if changed else "posts.json 변경 없음")

    if not args.posts_only:
        # 태그 반영된 posts로 graph.json 재생성
        update_graph(posts, force=False)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: extract_tags.py 삭제, tags_registry.json 삭제**

```bash
rm -f scripts/extract_tags.py
rm -f blog/tags_registry.json
```

- [ ] **Step 4: 통합 테스트 — init 실행**

Run: `cd /home/ahris/ahrism-pages/scripts && uv run python auto_tag.py init`
Expected: tags.json과 .tag_cache.json 생성, 태그 목록 출력

- [ ] **Step 5: 통합 테스트 — 전체 빌드**

Run: `cd /home/ahris/ahrism-pages/scripts && uv run python post_update.py`
Expected: posts.json, graph.json, tags.json 모두 정상 업데이트

- [ ] **Step 6: 커밋**

```bash
git add scripts/auto_tag.py scripts/post_update.py blog/tags.json
git rm -f scripts/extract_tags.py
git rm -f blog/tags_registry.json 2>/dev/null || true
git commit -m "feat: 자동 태그 시스템 통합 — 추천 + 생성 + 임베딩 캐시"
```

---

## Task 7: CLAUDE.md + .gitignore 업데이트

**Files:**
- Modify: `CLAUDE.md`
- Modify: `.gitignore`

- [ ] **Step 1: CLAUDE.md 파일 구조 및 옵션 테이블 업데이트**

반영 사항:
- `blog/tags.json` 설명 업데이트
- `blog/.tag_cache.json` 추가 (자동생성, gitignore)
- `auto_tag.py` 설명 업데이트
- `extract_tags.py` 제거
- `--suggest` 옵션 제거
- frontmatter에서 `tags` 필드 선택사항으로 변경

- [ ] **Step 2: .gitignore에 .tag_cache.json 추가**

```
blog/.tag_cache.json
```

- [ ] **Step 3: 커밋**

```bash
git add CLAUDE.md .gitignore
git commit -m "docs: CLAUDE.md 태그 시스템 문서 업데이트"
```

---

## 검증 체크리스트

- [ ] `uv run python auto_tag.py init` — tags.json + .tag_cache.json 생성
- [ ] `uv run python auto_tag.py suggest --all` — 전체 포스트 태그 추천 출력
- [ ] content.md에서 tags 제거 후 `uv run python post_update.py` — 태그 자동 할당 확인
- [ ] `blog/tags.json` 내용이 정규화된 태그 목록인지 확인
- [ ] `blog/.tag_cache.json`이 gitignore 되는지 확인
- [ ] `uv run pytest scripts/test_auto_tag.py -v` — 전체 테스트 통과
