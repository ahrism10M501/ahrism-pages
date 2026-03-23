# Blog Search & Graph Navigation Design

## Overview

ahrism 블로그에 검색 필터와 그래프 기반 포스트 탐색 기능을 추가한다. 순수 정적 사이트(GitHub Pages) 제약 하에서, 빌드 타임 Python 스크립트로 임베딩/유사도를 미리 계산하고 프론트엔드에서 소비한다.

## 요구사항

| 항목 | 설명 |
|------|------|
| 제목 유사도 검색 | 키워드 매칭 (기본) + TF-IDF 기반 의미 검색 (토글) |
| 태그 검색 | 태그 칩 클릭으로 필터링 (복수 선택, OR 조건) |
| 그래프 탐색 | Cytoscape.js로 포스트 간 유사도 그래프 시각화 |
| 포스트 추천 | 각 포스트 하단에 깊이 조절(2~5) 서브그래프 |

## 제약사항

- GitHub Pages 정적 사이트 — 서버 없음, 브라우저 ML 모델 로딩 불가
- 빌드 환경: RTX 3050 Laptop GPU (VRAM 4GB)
- 패키지 관리: uv

---

## 1. Python 빌드 스크립트 (`scripts/build_graph.py`)

### 입력
- `blog/posts.json` — 포스트 메타데이터
- `posts/<slug>/content.md` — 각 포스트 본문

### 처리 흐름
1. 모든 포스트의 제목 + 요약 + 본문(content.md) 읽기
2. `ko-sroberta-multitask` (sentence-transformers)로 포스트별 임베딩 생성
3. 모든 포스트 쌍의 cosine similarity 계산
4. threshold(예: 0.3) 이상인 쌍을 edge로 저장
5. scikit-learn `TfidfVectorizer`로 각 포스트에서 TF-IDF 상위 20개 키워드 추출
6. `blog/graph.json` 출력

### 의존성 (pyproject.toml)
- `sentence-transformers`
- `scikit-learn`
- `torch` (CUDA)

### 실행
```bash
cd scripts
uv run build_graph.py
```

### 출력: `blog/graph.json`
```json
{
  "nodes": [
    {
      "id": "hello-world",
      "title": "Hello World — 첫 번째 글",
      "date": "2026-03-23",
      "tags": ["blog"],
      "summary": "ahrism 블로그의 첫 번째 글입니다.",
      "tfidf": { "블로그": 0.45, "시작": 0.32 }
    }
  ],
  "edges": [
    { "source": "hello-world", "target": "other-post", "weight": 0.82 }
  ]
}
```

---

## 2. 블로그 페이지 (`blog/index.html`) 개편

### 레이아웃
```
┌─────────────────────────────────────┐
│ [검색바]  [의미검색 토글]            │
│ [태그1] [태그2] [태그3] ...         │
├─────────────────────────────────────┤
│ [◉ 그래프] [○ 리스트]  ← 뷰 토글   │
├─────────────────────────────────────┤
│                                     │
│   그래프 뷰 (기본)                   │
│   또는 리스트 뷰                     │
│                                     │
└─────────────────────────────────────┘
```

### 그래프 뷰 (Cytoscape.js)
- `graph.json`에서 노드/엣지 로드
- 노드 = 포스트 (제목 라벨), 엣지 = 유사도 (weight로 굵기/투명도)
- 노드 클릭 → 해당 포스트로 이동
- 검색/태그 필터 시 → 매칭 노드 하이라이트, 비매칭 노드 dim 처리

### 리스트 뷰
- 기존 `renderPostList`와 동일한 형태
- 검색/태그 필터 시 → 매칭 포스트만 표시

### 검색 동작
- **기본 모드:** 제목/요약 텍스트에 입력값 포함 여부로 필터
- **의미검색 토글 ON:** 입력 키워드를 각 노드의 `tfidf` 키와 매칭, 점수 합산으로 정렬/필터

### 태그 필터
- `graph.json` 노드에서 전체 태그 목록 추출, 칩 형태로 표시
- 클릭하면 활성/비활성 토글, 복수 선택 가능 (OR 조건)

---

## 3. 포스트 페이지 하단 서브그래프

### 배치
```
┌─────────────────────────────────────┐
│ 포스트 본문 (content.md)            │
├─────────────────────────────────────┤
│ 관련 글 탐색                        │
│ 깊이: ──●────── [2] [3] [4] [5]    │
│                                     │
│   (서브그래프: 현재 포스트 중심)      │
│                                     │
└─────────────────────────────────────┘
```

### 동작
- `graph.json`에서 현재 포스트를 루트로 BFS, 슬라이더 깊이만큼 탐색
- 루트 노드 강조 (primary 색상 `#dc00c9`), 나머지는 깊이에 따라 점점 dim
- 슬라이더 변경 시 실시간 서브그래프 재렌더링
- 노드 클릭 → 해당 포스트로 이동
- 초기 깊이: 2

---

## 4. 공용 그래프 모듈 (`graph.js`)

Cytoscape.js 렌더링/필터 로직을 공용 모듈로 분리:

### 주요 함수
- `initGraph(container, graphData, options)` — Cytoscape 인스턴스 생성 + 스타일 적용
- `filterGraph(cy, { query, tags, semantic })` — 검색/태그 필터 적용 (하이라이트/dim)
- `renderSubgraph(container, graphData, rootId, depth)` — 특정 노드 중심 서브그래프 렌더링
- `highlightMatches(cy, matchedIds)` — 매칭 노드 하이라이트

### 스타일
- 노드 색상: `#4a62ff` (secondary), 루트/하이라이트: `#dc00c9` (primary)
- 엣지 굵기/투명도: weight에 비례
- dim 처리: opacity 0.15

---

## 5. 파일 구조 변경

### 새로 추가
```
scripts/
  build_graph.py          # 임베딩 계산 + graph.json 생성
  pyproject.toml          # uv 프로젝트 의존성
blog/
  graph.json              # 빌드 산출물 (git 추적)
graph.js                  # Cytoscape.js 공용 모듈
```

### 수정
```
blog/index.html           # 그래프 뷰 + 리스트 뷰 토글, 검색/필터 UI
posts/_template/index.html # 하단 서브그래프 섹션 추가
style.css                 # 검색바, 태그 필터, 뷰 토글, 슬라이더 스타일
app.js                    # 검색/필터 로직 (키워드 + TF-IDF 매칭)
```

### CDN 추가
- Cytoscape.js (`blog/index.html`, `posts/_template/index.html`)

---

## 6. 빌드 워크플로

새 포스트 작성 시:
1. `posts/<slug>/content.md` 작성
2. `blog/posts.json`에 메타데이터 추가
3. `cd scripts && uv run build_graph.py` 실행
4. `blog/graph.json` 업데이트됨
5. git commit & push
