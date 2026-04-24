# Supernode Graph Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 태그 임베딩 계층적 군집화로 슈퍼노드를 자동 생성하고, Cytoscape.js 그래프에 다이아몬드 노드로 렌더링하며, 클릭 시 blog/?tags= 필터링 페이지로 이동하고, 엣지 호버 시 공유 태그 툴팁을 표시한다.

**Architecture:** `pipeline/supernode_builder.py`가 `.tag_cache.json`의 태그 임베딩을 AgglomerativeClustering으로 군집화해 슈퍼노드 목록을 생성, `graph.json`에 inject한다. `main.py` Stage 8로 통합된다. 프론트엔드 `graph.js`는 `supernodes` 배열을 읽어 diamond 노드를 추가하고, 클릭·툴팁 이벤트를 처리한다. 포스트 수 < 30이면 슈퍼노드 없이 기존 그래프만 렌더링된다.

**Tech Stack:** Python 3.10+, scikit-learn AgglomerativeClustering, numpy, Cytoscape.js, vanilla JS

---

### Task 1: 상수 및 모델 업데이트

**Files:**
- Modify: `pipeline/config.py`
- Modify: `pipeline/models.py`

- [ ] **Step 1: config.py에 슈퍼노드 상수 추가**

`pipeline/config.py` 파일 끝에 추가:
```python
# Supernode clustering
MIN_POSTS_FOR_SUPERNODES: int = 30   # 이 값에 도달하면 supernode_builder.py의 게이트 조건문 삭제
SUPERNODE_DISTANCE_THRESHOLD: float = 0.5
```

- [ ] **Step 2: models.py에 SupernodeData 추가 및 GraphData 확장**

`pipeline/models.py`에서 `GraphData` 클래스를 찾아 다음으로 교체:
```python
class SupernodeData(TypedDict):
    id: str
    label: str
    tags: list[str]


class _GraphDataRequired(TypedDict):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class GraphData(_GraphDataRequired, total=False):
    supernodes: list[SupernodeData]
```

- [ ] **Step 3: 변경 확인**

```bash
cd /home/ahris/ahrism-pages
python -c "from pipeline.config import MIN_POSTS_FOR_SUPERNODES, SUPERNODE_DISTANCE_THRESHOLD; print(MIN_POSTS_FOR_SUPERNODES, SUPERNODE_DISTANCE_THRESHOLD)"
python -c "from pipeline.models import SupernodeData, GraphData; print('OK')"
```
Expected:
```
30 0.5
OK
```

- [ ] **Step 4: 커밋**

```bash
git add pipeline/config.py pipeline/models.py
git commit -m "feat: add supernode constants and SupernodeData model"
```

---

### Task 2: pipeline/supernode_builder.py 생성 (TDD)

**Files:**
- Create: `tests/test_supernode_builder.py`
- Create: `pipeline/supernode_builder.py`

- [ ] **Step 1: 실패 테스트 작성**

`tests/test_supernode_builder.py` 신규 생성:
```python
"""Tests for pipeline.supernode_builder."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from pipeline import config


def _make_posts(n: int) -> list:
    """포스트 더미 데이터. 짝수는 AI 태그, 홀수는 하드웨어 태그."""
    return [
        {
            "slug": f"post-{i}",
            "title": f"Post {i}",
            "date": "2026-01-01",
            "tags": ["딥러닝", "신경망"] if i % 2 == 0 else ["하드웨어", "FPGA"],
        }
        for i in range(n)
    ]


def _make_tag_cache() -> dict:
    """공간적으로 두 군집이 명확한 태그 임베딩."""
    return {
        "딥러닝": [1.0, 0.0, 0.0],
        "신경망": [0.95, 0.05, 0.0],
        "하드웨어": [0.0, 0.0, 1.0],
        "FPGA": [0.05, 0.0, 0.95],
    }


def test_returns_empty_below_threshold(tmp_path):
    """포스트 수 < MIN_POSTS_FOR_SUPERNODES 이면 [] 반환, graph.json에 빈 배열 inject."""
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")

    from pipeline.supernode_builder import build_supernodes

    posts = _make_posts(5)  # 30 미만
    result = build_supernodes(posts, graph_path=graph_path)

    assert result == []
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    assert data["supernodes"] == []


def test_cluster_tags_groups_similar_tags(tmp_path):
    """유사한 태그들이 같은 슈퍼노드로 묶인다."""
    from pipeline.supernode_builder import _cluster_tags

    tag_cache = _make_tag_cache()
    posts = _make_posts(4)  # _cluster_tags는 직접 호출 — 게이트 없음

    with patch.object(config, "SUPERNODE_DISTANCE_THRESHOLD", 0.3):
        supernodes = _cluster_tags(tag_cache, posts)

    assert len(supernodes) >= 1
    all_tags = [t for s in supernodes for t in s["tags"]]
    assert set(all_tags) <= {"딥러닝", "신경망", "하드웨어", "FPGA"}
    # 각 슈퍼노드는 id, label, tags를 가짐
    for s in supernodes:
        assert "id" in s and "label" in s and "tags" in s
        assert isinstance(s["tags"], list)


def test_inject_supernodes_writes_to_graph_json(tmp_path):
    """_inject_supernodes_into_graph이 graph.json의 supernodes 키를 덮어쓴다."""
    from pipeline.supernode_builder import _inject_supernodes_into_graph

    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps({"nodes": [{"id": "nn1"}], "edges": []}), encoding="utf-8"
    )
    supernodes = [{"id": "supernode-0", "label": "딥러닝", "tags": ["딥러닝", "신경망"]}]

    _inject_supernodes_into_graph(supernodes, graph_path=graph_path)

    data = json.loads(graph_path.read_text(encoding="utf-8"))
    assert data["supernodes"] == supernodes
    assert data["nodes"] == [{"id": "nn1"}]  # 기존 노드 유지


def test_build_supernodes_runs_clustering_above_threshold(tmp_path):
    """포스트 수 >= 30이면 tag_cache 기반 클러스터링이 실행된다."""
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")

    from pipeline.supernode_builder import build_supernodes

    posts = _make_posts(30)
    tag_cache = _make_tag_cache()

    with patch("pipeline.supernode_builder.io.load_tag_cache", return_value=tag_cache), \
         patch.object(config, "SUPERNODE_DISTANCE_THRESHOLD", 0.3):
        result = build_supernodes(posts, graph_path=graph_path)

    assert len(result) >= 1
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    assert len(data["supernodes"]) == len(result)
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

```bash
cd /home/ahris/ahrism-pages
uv run pytest tests/test_supernode_builder.py -v 2>&1 | head -30
```
Expected: `ModuleNotFoundError: No module named 'pipeline.supernode_builder'` (또는 import 오류)

- [ ] **Step 3: pipeline/supernode_builder.py 구현**

`pipeline/supernode_builder.py` 신규 생성:
```python
"""
Builds supernodes (thematic anchors) from tag embeddings via agglomerative clustering.
Injects `supernodes` array into graph.json after graph construction.

Gate: skips clustering if post count < config.MIN_POSTS_FOR_SUPERNODES.
TODO: 포스트가 30개 이상이 되면 build_supernodes()의 게이트 조건문 전체를 삭제할 것.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import normalize

from pipeline import config, io
from pipeline.models import PostRecord, SupernodeData, TagCache


def build_supernodes(
    posts: list[PostRecord],
    graph_path: Path | None = None,
) -> list[SupernodeData]:
    """
    포스트 수 < MIN_POSTS_FOR_SUPERNODES이면 빈 supernodes를 graph.json에 inject 후 반환.
    이상이면 tag_cache 임베딩을 AgglomerativeClustering으로 군집화해 슈퍼노드 생성.
    """
    if len(posts) < config.MIN_POSTS_FOR_SUPERNODES:
        # TODO: 포스트가 30개 이상이 되면 이 조건문 전체를 삭제할 것
        _inject_supernodes_into_graph([], graph_path)
        return []

    tag_cache = io.load_tag_cache()
    supernodes = _cluster_tags(tag_cache, posts)
    _inject_supernodes_into_graph(supernodes, graph_path)
    print(f"슈퍼노드 생성 완료 ({len(supernodes)}개 클러스터)")
    return supernodes


def _cluster_tags(
    tag_cache: TagCache,
    posts: list[PostRecord],
) -> list[SupernodeData]:
    """태그 임베딩을 AgglomerativeClustering으로 군집화해 SupernodeData 목록 반환."""
    all_post_tags = [tag for p in posts for tag in p.get("tags", [])]
    tag_freq = Counter(all_post_tags)

    # 포스트에 등장하고 임베딩이 있는 태그만 사용
    known_tags = [t for t in tag_freq if t in tag_cache]
    if len(known_tags) < 2:
        return []

    embeddings = np.array([tag_cache[t] for t in known_tags], dtype=np.float32)
    # cosine distance를 위해 L2 정규화
    embeddings = normalize(embeddings, norm="l2")

    model = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=config.SUPERNODE_DISTANCE_THRESHOLD,
        linkage="average",
        metric="cosine",
    )
    labels = model.fit_predict(embeddings)

    clusters: dict[int, list[str]] = {}
    for tag, label in zip(known_tags, labels.tolist()):
        clusters.setdefault(label, []).append(tag)

    supernodes: list[SupernodeData] = []
    for cluster_id, tags in sorted(clusters.items()):
        label = max(tags, key=lambda t: tag_freq[t])
        supernodes.append({
            "id": f"supernode-{cluster_id}",
            "label": label,
            "tags": sorted(tags, key=lambda t: -tag_freq[t]),
        })

    return supernodes


def _inject_supernodes_into_graph(
    supernodes: list[SupernodeData],
    graph_path: Path | None = None,
) -> None:
    """graph.json을 읽어 supernodes 키를 upsert하고 원자적으로 저장."""
    target = graph_path or config.GRAPH_JSON
    graph = io.load_json(target, default={"nodes": [], "edges": [], "supernodes": []})
    graph["supernodes"] = supernodes
    io.save_graph_json(graph, target)
```

- [ ] **Step 4: 테스트 실행해서 통과 확인**

```bash
cd /home/ahris/ahrism-pages
uv run pytest tests/test_supernode_builder.py -v
```
Expected:
```
PASSED tests/test_supernode_builder.py::test_returns_empty_below_threshold
PASSED tests/test_supernode_builder.py::test_cluster_tags_groups_similar_tags
PASSED tests/test_supernode_builder.py::test_inject_supernodes_writes_to_graph_json
PASSED tests/test_supernode_builder.py::test_build_supernodes_runs_clustering_above_threshold
4 passed
```

- [ ] **Step 5: 기존 테스트 회귀 확인**

```bash
cd /home/ahris/ahrism-pages
uv run pytest tests/ -v
```
Expected: 전체 PASSED (새 4개 포함)

- [ ] **Step 6: 커밋**

```bash
git add pipeline/supernode_builder.py tests/test_supernode_builder.py
git commit -m "feat: add supernode_builder with agglomerative tag clustering"
```

---

### Task 3: main.py Stage 8 통합

**Files:**
- Modify: `main.py`

- [ ] **Step 1: import 추가**

`main.py`의 import 블록:
```python
from pipeline import config, embedder, graph_builder, io, scanner, state, tagger
from pipeline.models import RunState
```
를 다음으로 교체:
```python
from pipeline import config, embedder, graph_builder, io, scanner, state, supernode_builder, tagger
from pipeline.models import RunState
```

- [ ] **Step 2: Stage 8 추가**

`main.py`의 `run_pipeline` 함수에서 `return run_state` 바로 위의 이 블록:
```python
    if not posts_only:
        # Re-build graph with normalised tags from stage 5
        cache = io.load_post_cache()
        graph_builder.build_graph(posts, cache)

    return run_state
```
를 다음으로 교체:
```python
    if not posts_only:
        # Re-build graph with normalised tags from stage 5
        cache = io.load_post_cache()
        graph_builder.build_graph(posts, cache)

        # Stage 8: supernodes
        print("슈퍼노드 군집화 중...")
        supernode_builder.build_supernodes(posts)

    return run_state
```

- [ ] **Step 3: 파이프라인 실행 확인**

```bash
cd /home/ahris/ahrism-pages
uv run python main.py --posts-only
```
Expected: 오류 없이 완료 (`--posts-only`는 Stage 8 스킵).

```bash
uv run python main.py 2>&1 | tail -10
```
Expected: `슈퍼노드 군집화 중...` 출력 + `=== 파이프라인 완료 ===`

- [ ] **Step 4: graph.json supernodes 키 확인**

```bash
python -c "import json; d=json.load(open('blog/graph.json')); print('supernodes' in d, len(d.get('supernodes', [])))"
```
Expected: `True 0` (포스트 30개 미만이므로 빈 배열)

- [ ] **Step 5: 커밋**

```bash
git add main.py
git commit -m "feat: integrate supernode Stage 8 into main pipeline"
```

---

### Task 4: graph.js — 슈퍼노드 렌더링 + 엣지 툴팁

**Files:**
- Modify: `graph.js`

- [ ] **Step 1: initGraph() 상단에 슈퍼노드 elements 추가**

`graph.js`의 `initGraph` 함수에서 `for (const edge of graphData.edges) {` 루프 **이후**, `const cy = cytoscape({` **이전**에 다음 블록 삽입:

```javascript
  // 슈퍼노드 추가 (supernodes 배열이 있을 때만)
  if (Array.isArray(graphData.supernodes) && graphData.supernodes.length > 0) {
    for (const sn of graphData.supernodes) {
      elements.push({
        group: 'nodes',
        data: { id: sn.id, label: sn.label, tags: sn.tags, isSupernode: true },
        classes: 'supernode',
      });
    }
  }
```

- [ ] **Step 2: Cytoscape 스타일시트에 슈퍼노드 스타일 추가**

`graph.js`의 `style: [` 배열 맨 끝 `],` 바로 앞에 다음 추가:

```javascript
      {
        selector: 'node.supernode',
        style: {
          'shape': 'diamond',
          'width': 48,
          'height': 48,
          'background-color': '#1a0018',
          'border-color': '#dc00c9',
          'border-width': 2,
          'label': 'data(label)',
          'font-size': '11px',
          'color': '#dc00c9',
          'text-valign': 'center',
          'text-halign': 'center',
          'text-wrap': 'ellipsis',
          'text-max-width': '60px',
          'z-index': 10,
        },
      },
      {
        selector: 'node.supernode.dimmed',
        style: { 'opacity': 0.2 },
      },
```

- [ ] **Step 3: 노드 클릭 핸들러를 슈퍼노드 분기 처리로 교체**

기존:
```javascript
  // 노드 클릭 이벤트
  if (options.onNodeClick) {
    cy.on('tap', 'node', function (evt) {
      options.onNodeClick(evt.target.data('id'));
    });
  }
```
를 다음으로 교체:
```javascript
  // 노드 클릭 이벤트
  cy.on('tap', 'node', function (evt) {
    const node = evt.target;
    if (node.hasClass('supernode')) {
      const tags = node.data('tags');
      if (Array.isArray(tags) && tags.length > 0) {
        window.location.href = '/blog/index.html?tags=' + tags.map(encodeURIComponent).join(',');
      }
      return;
    }
    if (options.onNodeClick) {
      options.onNodeClick(node.data('id'));
    }
  });
```

- [ ] **Step 4: applyDepthEffect()에서 슈퍼노드 제외**

`applyDepthEffect` 함수의 `const nodes = cy.nodes();` 다음 줄을 교체:

기존:
```javascript
  const nodes = cy.nodes();
  if (nodes.length === 0) return;
```
교체 후:
```javascript
  const nodes = cy.nodes().filter(n => !n.hasClass('supernode'));
  if (nodes.length === 0) return;
```

- [ ] **Step 5: setupHoverHighlight()에서 슈퍼노드 호버 스킵**

`setupHoverHighlight` 함수의 `cy.on('mouseover', 'node', function (evt) {` 핸들러 맨 첫 줄에 추가:

기존:
```javascript
  cy.on('mouseover', 'node', function (evt) {
    if (cy._searchHighlightActive) return;
```
교체 후:
```javascript
  cy.on('mouseover', 'node', function (evt) {
    if (cy._searchHighlightActive) return;
    if (evt.target.hasClass('supernode')) return;
```

- [ ] **Step 6: 엣지 툴팁 함수 추가 및 초기화**

`graph.js` 파일 맨 끝 (`applyDepthEffect` 함수 닫는 `}` 다음)에 추가:

```javascript
/**
 * Show a tooltip near the mouse with shared tags when hovering an edge.
 * @param {Object} cy - Cytoscape instance
 * @param {HTMLElement} container - Graph container DOM element
 */
function setupEdgeTooltip(cy, container) {
  const tip = document.createElement('div');
  tip.id = 'edge-tooltip';
  tip.style.cssText = [
    'position:fixed',
    'display:none',
    'background:#111111',
    'border:1px solid #1e1e1e',
    'color:#cccccc',
    'font-size:11px',
    'padding:4px 8px',
    'pointer-events:none',
    'z-index:9999',
    'white-space:nowrap',
  ].join(';');
  document.body.appendChild(tip);

  cy.on('mouseover', 'edge', function (evt) {
    const edge = evt.target;
    const srcTags = new Set(edge.source().data('tags') || []);
    const tgtTags = (edge.target().data('tags') || []).filter(t => srcTags.has(t));
    if (tgtTags.length === 0) return;

    tip.textContent = tgtTags.map(t => '#' + t).join('  ');
    tip.style.display = 'block';
  });

  cy.on('mousemove', 'edge', function (evt) {
    if (tip.style.display === 'none') return;
    tip.style.left = (evt.originalEvent.clientX + 12) + 'px';
    tip.style.top = (evt.originalEvent.clientY - 8) + 'px';
  });

  cy.on('mouseout', 'edge', function () {
    tip.style.display = 'none';
  });
}
```

그리고 `initGraph` 함수의 `return cy;` 바로 위에 추가:
```javascript
  setupEdgeTooltip(cy, container);

  return cy;
```

- [ ] **Step 7: 로컬 서버에서 그래프 동작 확인**

```bash
cd /home/ahris/ahrism-pages
python3 -m http.server 8080
```
브라우저에서 `http://localhost:8080/blog/` 열기:
- 그래프 뷰 전환 확인
- 일반 포스트 노드 클릭 → `posts/<slug>/` 이동 확인
- 엣지 위에 마우스 올리면 공유 태그 툴팁 나타남 확인
- 슈퍼노드는 포스트 수 < 30이라 렌더링 안 됨 — 오류 없음 확인

- [ ] **Step 8: 커밋**

```bash
git add graph.js
git commit -m "feat: add supernode rendering, click navigation, and edge tag tooltip"
```

---

### Task 5: blog/index.html — URL 파라미터 태그 필터링

**Files:**
- Modify: `blog/index.html`

- [ ] **Step 1: URL 파라미터 파싱 코드 삽입**

`blog/index.html`에서 `allTags.forEach(tag => {` 루프의 닫는 `});` (태그 칩 생성 루프 끝) 바로 **다음** 줄에 삽입:

```javascript
      // URL ?tags= 파라미터로 태그 필터 자동 적용
      const urlParams = new URLSearchParams(window.location.search);
      const urlTagParam = urlParams.get('tags');
      if (urlTagParam) {
        const urlTags = urlTagParam.split(',').map(decodeURIComponent);
        allChip.classList.remove('active');
        document.querySelectorAll('.tag--filter:not([data-all])').forEach(chip => {
          if (urlTags.includes(chip.textContent)) {
            chip.classList.add('active');
          }
        });
        const anyActive = [...document.querySelectorAll('.tag--filter:not([data-all]).active')].length > 0;
        if (!anyActive) allChip.classList.add('active');
        applyFilters();
      }
```

- [ ] **Step 2: 로컬 서버에서 URL 파라미터 동작 확인**

```bash
cd /home/ahris/ahrism-pages
python3 -m http.server 8080
```
브라우저에서 `http://localhost:8080/blog/index.html?tags=딥러닝,신경망` 열기.
Expected: 페이지 로드 시 "딥러닝", "신경망" 태그 칩이 active 상태로 표시되고 필터 적용됨.

- [ ] **Step 3: 커밋**

```bash
git add blog/index.html
git commit -m "feat: parse URL ?tags= param and apply tag filter on blog page load"
```

---

### Task 6: 문서 생성

**Files:**
- Create: `docs/supernode-activation.md`
- Create: `docs/backlog-next-sessions.md`

- [ ] **Step 1: supernode-activation.md 생성**

`docs/supernode-activation.md` 신규 생성:
```markdown
# 슈퍼노드 활성화 가이드

## 현재 상태

슈퍼노드 기능은 구현되어 있지만 **포스트 수 30개 미만이면 비활성**입니다.
`blog/graph.json`의 `supernodes` 배열이 비어 있으면 그래프는 기존 포스트 노드만 렌더링합니다.

## 활성화 조건

포스트가 30개 이상이 되면 아래 두 곳의 게이트 조건문을 삭제하세요.

### 1. `pipeline/supernode_builder.py` — `build_supernodes()` 함수

```python
# 삭제 대상:
if len(posts) < config.MIN_POSTS_FOR_SUPERNODES:
    # TODO: 포스트가 30개 이상이 되면 이 조건문 전체를 삭제할 것
    _inject_supernodes_into_graph([], graph_path)
    return []
```

### 2. `pipeline/config.py`

`MIN_POSTS_FOR_SUPERNODES` 상수도 필요에 따라 제거하거나 값 조정.

## 활성화 후 확인

```bash
uv run python main.py --force
python -c "import json; d=json.load(open('blog/graph.json')); print(len(d['supernodes']), '개 슈퍼노드')"
```

그래프에서 magenta 다이아몬드 노드를 클릭하면 해당 주제 태그로 필터링된 블로그 페이지로 이동합니다.

## 관련 파라미터 (`pipeline/config.py`)

| 상수 | 기본값 | 설명 |
|------|--------|------|
| `MIN_POSTS_FOR_SUPERNODES` | 30 | 슈퍼노드 활성화 최소 포스트 수 |
| `SUPERNODE_DISTANCE_THRESHOLD` | 0.5 | 클러스터 granularity (낮을수록 더 많은 클러스터) |
```

- [ ] **Step 2: backlog-next-sessions.md 생성**

`docs/backlog-next-sessions.md` 신규 생성:
```markdown
# 다음 세션 백로그

슈퍼노드 그래프 고도화 이후 구현 예정 기능들입니다.

---

## B — UI/UX 디테일

**우선순위:** 중 (독립적, 범위 작음)

### B-1: IPYNB Matplotlib 다크모드 동기화
- `.ipynb` 뷰어에서 차트/그래프 이미지가 흰 배경으로 나오는 문제
- 해결책 옵션:
  - 노트북 작성 시 `plt.style.use('dark_background')` 강제하는 가이드 문서 추가
  - 또는 CSS `img.cell-output-image { filter: invert(0.9) hue-rotate(180deg); }` 적용 (Matplotlib 이미지에만)

### B-2: 터미널 스타일 로딩 UI
- 현재 `.ipynb` 로딩 시 단순 `Loading...` 텍스트
- 개선: `[INFO] Fetching notebook data...` + 깜빡이는 커서 애니메이션
- 관련 파일: `posts/_template/index.html`, CSS `@keyframes` 추가

---

## C — Twinkle 공간

**우선순위:** 높 (새로운 콘텐츠 레이어)

짧은 단상·디버깅 기록·아이디어 스케치 전용 섹션. 긴 포스트와 분리된 경량 콘텐츠 공간.

### 구현 고려사항
- 새 콘텐츠 타입 → `posts.json` 스키마에 `type: "twinkle"` 필드 추가
- 별도 라우팅: `/twinkle/` 또는 blog 내 탭
- Frontmatter: `type: twinkle`, 본문 < 500자 제한 권장
- 그래프에 포함할지 여부 결정 필요 (별도 그래프 vs 메인 그래프에 다른 스타일로 포함)

---

## D — 포트폴리오 연결

**우선순위:** 중 (태그 시스템 활용)

About 페이지의 기술 스택(Python, PyTorch, Verilog 등) 클릭 → 관련 포스트/프로젝트만 그래프/리스트로 필터링.

### 구현 고려사항
- `index.html` About 섹션의 기술 스택 항목에 `data-tag` 속성 추가
- 클릭 시 `/blog/index.html?tags=<skill>` 이동 (Task 5의 URL 파라미터 기능 활용)
- `projects.json`에도 `tags` 필드 추가해 프로젝트 카드 필터링 연동
```

- [ ] **Step 3: 커밋**

```bash
git add docs/supernode-activation.md docs/backlog-next-sessions.md
git commit -m "docs: add supernode activation guide and next-session backlog"
```

---

## 전체 검증

- [ ] `uv run pytest tests/ -v` — 전체 테스트 통과 확인
- [ ] `uv run python main.py` — 파이프라인 정상 완료, `blog/graph.json`에 `supernodes: []` 확인
- [ ] `python3 -m http.server 8080` 후 브라우저 검증:
  - `http://localhost:8080/` — 랜딩 그래프 정상 렌더링
  - `http://localhost:8080/blog/` — 그래프 뷰에서 엣지 호버 툴팁 동작
  - `http://localhost:8080/blog/index.html?tags=딥러닝` — 태그 자동 필터링
  - 일반 노드 클릭 → `posts/<slug>/` 이동
