# Design System Unification

**Date:** 2026-03-28
**Scope:** 사이트 전반 공통 테마 정리 — 일관성 확보 후 polish

---

## 목표

현재 페이지마다 불일치하는 태그·레이블·border-radius를 하나의 디자인 토큰 시스템으로 통합한다. CSS 클래스 중복을 제거하고 HTML도 함께 정리한다.

---

## 디자인 토큰

### 태그 칩

| 상태 | 스타일 |
|------|--------|
| 읽기 전용 (`.tag`) | `[텍스트]` bracket 형태, 색상 `#555`, bracket `#2a2a2a`, 배경 없음 |
| 필터 비활성 (`.tag--filter`) | outline border `#222`, 텍스트 `#444` |
| 필터 활성 (`.tag--filter.active`) | border `rgba(74,98,255,0.5)`, 텍스트 `#4a62ff`, 배경 `rgba(74,98,255,0.07)` |

`.tag`와 `.tag-filter`를 각각 `.tag`와 `.tag--filter`로 통합. 기존 `.tag-filter` 클래스 제거.

### 레이블

**`.label`** — 섹션 구분선 레이블 (Blog, GitHub, 프로젝트, 학력 등)
- 폰트: `0.65rem`, 회색 `#444`, uppercase, `letter-spacing: 2px`
- 하단: `border-bottom: 1px solid #1e1e1e`
- 마젠타 accent: `::after { width: 24px; height: 1px; background: #dc00c9; bottom: -1px }`

기존 `.section-label`, `.editorial-label`, `.panel-header`, `.gh-source-label` 모두 `.label`로 통합.

**`.label--slash`** — editorial-header 내부 인라인 레이블 (About 섹션 전용)
- `/ 텍스트` 형태: `::before { content: '/ '; color: #dc00c9; font-weight: 600 }`
- 텍스트: `#555`, uppercase, `letter-spacing: 2px`
- border 없음

### Editorial Header

`.editorial-header`의 `border-left` 색상: `#dc00c9` → **`#ff0000`**
(사이트에서 유일하게 빨간 accent를 쓰는 지점 — 최강 강조)

### Border-radius

모든 요소 **0px**으로 통일.
대상: 카드(`.project-card`, `.gh-repo-card`), 입력창(`.search-bar input`), 버튼(`.view-toggle button`, `.zoom-preset`), 태그 칩, 코드 블록(`.post-content pre`), 그래프 컨테이너(`.graph-container`)

---

## 변경 범위

### style.css

1. `.tag` — bracket 스타일로 교체 (`::before`, `::after` pseudo-element)
2. `.tag-filter` → `.tag--filter` — outline 스타일로 교체, 기존 규칙 제거
3. `.section-label`, `.editorial-label`, `.panel-header`, `.gh-source-label` 규칙 제거 → `.label`로 통합
4. `.label--slash` 신규 추가
5. `.editorial-header` border-left 색상 → `#ff0000`
6. 전체 `border-radius` 값 → `0`

### HTML 파일 (클래스 교체)

| 파일 | 변경 내용 |
|------|-----------|
| `index.html` | `.editorial-label` → `.label--slash`, `.section-label` → `.label` |
| `blog/index.html` | `.tag-filter` → `.tag--filter` |
| `github/index.html` | `.gh-source-label` → `.label` |
| `posts/_template/index.html` | 태그 출력 클래스 `.tag` 유지 (렌더링은 JS가 담당) |

### app.js / post.js (태그 렌더링)

`renderPostList`가 태그를 `.tag` 클래스로 생성하는 부분: bracket pseudo-element는 CSS가 처리하므로 클래스명만 `.tag` 유지하면 됨. JS 변경 최소화.

---

## 변경하지 않는 것

- 사이드바 구조 및 색상 (마젠타 left-border active 상태 유지)
- 색상 팔레트 (`#dc00c9`, `#4a62ff`, `#ff0000`, `#0a0a0a`, `#111`, `#1e1e1e`)
- 그래프 시각화 (graph.js, Cytoscape 스타일)
- 타이포그래피 크기 체계
- 레이아웃 구조

---

## 성공 기준

- 모든 페이지에서 태그가 동일한 `[bracket]` 스타일로 보임
- 레이블 클래스가 `.label` / `.label--slash` 두 가지만 존재
- border-radius 값이 style.css 전체에서 `0` 또는 `0px`만 사용됨 (zoom-preset `50%` 제외 검토)
- 기존 삭제된 클래스명이 HTML에 남아있지 않음
