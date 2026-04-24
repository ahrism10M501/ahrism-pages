# 슈퍼노드 그래프 고도화 — 설계 문서

**날짜:** 2026-04-24  
**상태:** 설계 완료, 구현 대기

---

## Context

포스트 수가 늘어남에 따라 그래프가 복잡해지면서 주제별 탐색이 어려워진다. 슈퍼노드(주제 거점)를 도입해 방문자가 원하는 성격의 글을 직관적으로 찾아갈 수 있도록 한다. 단, 현재 포스트 수가 적어 효과가 제한적이므로 30포스트 임계값 게이트를 두고, 조건이 충족되면 코드에서 게이트를 제거한다.

---

## 범위

- `pipeline/supernode_builder.py` 신규 생성 (태그 임베딩 계층적 군집화)
- `main.py` Stage 8 추가 (슈퍼노드 빌드 → graph.json inject)
- `pipeline/config.py` 상수 추가
- `blog/graph.json` 스키마 확장 (`supernodes` 배열)
- `graph.js` 슈퍼노드 렌더링 + 엣지 툴팁
- `blog/index.html` URL 파라미터 태그 필터링 지원

---

## 아키텍처

### 파이프라인 (`main.py`)

```
Stage 1: 포스트 스캔
Stage 2: stale 탐지
Stage 3: 임베딩 계산
Stage 4: graph.json 빌드
Stage 5: 태그 자동 할당 (tags.json)
Stage 6: posts.json 저장
Stage 7: 태그 반영 graph.json 재빌드
Stage 8 (신규): 슈퍼노드 빌드 → graph.json inject
```

Stage 8은 태그가 최종 확정된 뒤 실행. `graph_builder.py`는 변경 없음.
`supernode_builder.build_supernodes(posts)` — 내부에서 tag_cache 직접 로드.

### `pipeline/supernode_builder.py`

```python
def build_supernodes(posts: list) -> list[dict]:
    """
    포스트 수 < MIN_POSTS_FOR_SUPERNODES 이면 [] 반환.
    io.load_tag_cache()로 .tag_cache.json(태그 임베딩)을 로드한 뒤
    AgglomerativeClustering 적용 → graph.json의 supernodes 키에 inject.
    """
```

**태그 임베딩 출처:** `.tag_cache.json` — `io.load_tag_cache()`로 로드. 포스트 임베딩(`.post_cache.json`)과 별개.

**클러스터링:**
- `sklearn.cluster.AgglomerativeClustering(n_clusters=None, distance_threshold=SUPERNODE_DISTANCE_THRESHOLD, linkage='average')`
- 클러스터 label = 해당 클러스터 내 빈도 가장 높은 태그명
- 슈퍼노드→포스트 엣지는 graph.json에 포함하지 않음 (레이아웃 힌트 불필요)

---

## 데이터 스키마

### `blog/graph.json` 변경

```json
{
  "nodes": [...],
  "edges": [...],
  "supernodes": [
    {
      "id": "supernode-0",
      "label": "딥러닝",
      "tags": ["딥러닝", "신경망", "트랜스포머"]
    }
  ]
}
```

포스트 수 < 30이면 `"supernodes": []`.

### `pipeline/config.py` 신규 상수

```python
MIN_POSTS_FOR_SUPERNODES = 30   # 이 값에 도달하면 아래 게이트 코드 삭제 참조
SUPERNODE_DISTANCE_THRESHOLD = 0.5
```

---

## 프론트엔드 (`graph.js`)

### 슈퍼노드 렌더링

- `initGraph()` 진입부: `data.supernodes`가 비어 있으면 슈퍼노드 단계 전체 스킵
- Cytoscape `node.supernode` 스타일:
  - `shape: 'diamond'`
  - `width: 48, height: 48`
  - `border-color: #dc00c9, border-width: 2`
  - `background-color: #1a0018`
  - `label: data(label), font-size: 11, color: #dc00c9`
- 슈퍼노드는 fcose 레이아웃 물리 계산에서 제외 (`locked: true`)

### 슈퍼노드 클릭

```
cy.on('tap', 'node.supernode') →
  tags = node.data('tags')
  window.location = '/blog/index.html?tags=' + tags.join(',')
```

### 엣지 툴팁 (공유 태그)

```
cy.on('mouseover', 'edge') →
  sharedTags = source.tags ∩ target.tags
  sharedTags 있으면 → 포인터 위치에 absolute div 툴팁 표시
  예: #딥러닝  #신경망

cy.on('mouseout', 'edge') → 툴팁 제거
```

공유 태그 없으면 툴팁 미표시.

---

## `blog/index.html` URL 파라미터 지원

페이지 로드 시:
```javascript
const params = new URLSearchParams(window.location.search)
const tagsParam = params.get('tags')
if (tagsParam) {
  // tagsParam.split(',') → activeTags 세팅 → applyFilters() 호출
}
```

기존 `applyFilters()` 로직 재사용, 태그 칩 UI도 파라미터 기반으로 active 상태 표시.

---

## 30포스트 게이트

**`pipeline/supernode_builder.py`:**
```python
if len(posts) < config.MIN_POSTS_FOR_SUPERNODES:
    # 포스트가 30개 미만 — 슈퍼노드 비활성
    # TODO: 포스트가 30개 이상이 되면 이 조건문 전체를 삭제할 것
    _inject_empty_supernodes()
    return []
```

**`graph.js`:**
```javascript
if (!data.supernodes || data.supernodes.length === 0) {
    // 슈퍼노드 없음 — 기존 그래프만 렌더링
    // TODO: 포스트가 30개 이상이 되면 이 조건문 전체를 삭제할 것
    return
}
```

---

## 검증 방법

1. `uv run python main.py` 실행 → `blog/graph.json`에 `supernodes` 키 확인
2. 포스트 수 < 30 상태에서 → `supernodes: []` 확인
3. `python3 -m http.server 8080` → `http://localhost:8080/` 그래프 로드
4. 슈퍼노드 없을 때 기존 그래프 정상 동작 확인
5. (포스트 30개 이후) 다이아몬드 노드 렌더링 확인
6. 슈퍼노드 클릭 → `blog/index.html?tags=...` 이동 + 태그 필터 자동 적용 확인
7. 엣지 호버 → 공유 태그 툴팁 표시 확인

---

## 관련 파일

| 파일 | 변경 유형 |
|------|---------|
| `pipeline/supernode_builder.py` | 신규 생성 |
| `main.py` | Stage 8 추가 |
| `pipeline/config.py` | 상수 2개 추가 |
| `blog/graph.json` | 스키마 확장 (자동생성) |
| `graph.js` | 슈퍼노드 렌더링 + 엣지 툴팁 추가 |
| `blog/index.html` | URL 파라미터 태그 필터 추가 |
| `docs/supernode-activation.md` | 신규 (게이트 결정 기록) |
| `docs/backlog-next-sessions.md` | 신규 (다음 세션 백로그) |
