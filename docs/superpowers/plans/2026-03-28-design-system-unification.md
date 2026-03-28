# Design System Unification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `style.css`의 태그·레이블·border-radius를 통합 토큰 시스템으로 교체하고, 4개 HTML 파일 + 8개 포스트 파일의 클래스명을 일치시킨다.

**Architecture:** CSS 규칙을 먼저 교체(Task 1-3), 이후 HTML/JS 클래스명을 파일별로 갱신(Task 4-8), 마지막으로 구 클래스명 잔재 검증(Task 9). 각 Task 후 커밋.

**Tech Stack:** 순수 HTML/CSS, 로컬 서버 `python3 -m http.server 8080`으로 시각 검증.

---

## 파일 맵

| 파일 | 변경 내용 |
|------|-----------|
| `style.css` | `.tag` bracket, `.tag--filter` 신규, `.label` 통합, `.label--slash` 신규, editorial-header 빨강, border-radius 0px |
| `index.html` | `panel-header`→`label`, `editorial-label`→`label--slash` |
| `blog/index.html` | `panel-header`→`label`, JS 내 `tag-filter`→`tag--filter` 5곳 |
| `github/index.html` | `panel-header`→`label`, `editorial-label`→`label--slash` |
| `posts/_template/index.html` | `panel-header`→`label`, `section-label`→`label` |
| `posts/*/index.html` (8개) | 위와 동일 (batch sed) |

---

## Task 1: style.css — 태그 스타일 교체

**Files:**
- Modify: `style.css`

- [ ] **Step 1: `.tag` 규칙을 bracket 스타일로 교체**

`style.css`의 기존 `.tag { ... }` 블록 전체를 아래로 교체:

```css
/* Tag chips */
.tag {
  display: inline-block;
  font-size: 0.72rem;
  color: #555;
}
.tag::before {
  content: '[';
  color: #2a2a2a;
  margin-right: 1px;
}
.tag::after {
  content: ']';
  color: #2a2a2a;
  margin-left: 1px;
}
```

- [ ] **Step 2: `.tag--filter` 규칙 추가 (`.tag` 블록 바로 아래)**

```css
.tag--filter {
  display: inline-block;
  font-size: 0.72rem;
  color: #444;
  border: 1px solid #222;
  padding: 0.12rem 0.45rem;
  cursor: pointer;
  transition: color 0.12s, border-color 0.12s, background 0.12s;
}
.tag--filter:hover {
  color: #777;
  border-color: #444;
}
.tag--filter.active {
  color: #4a62ff;
  border-color: rgba(74, 98, 255, 0.5);
  background: rgba(74, 98, 255, 0.07);
}
```

- [ ] **Step 3: 기존 `.tag-filter` 관련 규칙 전체 삭제**

`style.css`에서 아래 블록들을 삭제:
- `.tag-filter { ... }` 블록
- `.tag-filter.active { ... }` 블록

- [ ] **Step 4: 시각 확인**

```bash
python3 -m http.server 8080
```

`http://localhost:8080/blog/` 접속 → 포스트 태그가 `[딥러닝]` 형태로 보이는지 확인. 필터 칩은 아직 JS 클래스명이 구버전이므로 안 보임 — 정상.

- [ ] **Step 5: 커밋**

```bash
git add style.css
git commit -m "style: tag chip → bracket style, add tag--filter"
```

---

## Task 2: style.css — 레이블 통합 + editorial-header 빨강

**Files:**
- Modify: `style.css`

- [ ] **Step 1: 기존 레이블 클래스 5개 삭제**

`style.css`에서 아래 블록들을 삭제:
- `.section-label { ... }` 블록
- `.editorial-label { ... }` 블록
- `.panel-header { ... }` 블록
- `.gh-source-label { ... }` 블록

- [ ] **Step 2: `.label` 통합 클래스 추가**

삭제한 자리에 아래 추가:

```css
/* Section label (unified) */
.label {
  font-size: 0.65rem;
  color: #444;
  text-transform: uppercase;
  letter-spacing: 2px;
  display: block;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid #1e1e1e;
  position: relative;
  margin-bottom: 1rem;
}
.label::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 24px;
  height: 1px;
  background: #dc00c9;
}

/* Slash label — editorial-header 내부 전용 */
.label--slash {
  font-size: 0.62rem;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 2px;
  display: block;
  margin-bottom: 0.25rem;
}
.label--slash::before {
  content: '/ ';
  color: #dc00c9;
  font-weight: 600;
  letter-spacing: 0;
}
```

- [ ] **Step 3: `.editorial-header` border-left 색상 변경**

`style.css`의 `.editorial-header` 블록에서:
```css
border-left: 2px solid var(--pico-primary);
```
→
```css
border-left: 2px solid #ff0000;
```

- [ ] **Step 4: 커밋**

```bash
git add style.css
git commit -m "style: unify label classes, editorial-header → red"
```

---

## Task 3: style.css — border-radius 0px 전체

**Files:**
- Modify: `style.css`

- [ ] **Step 1: 카드·컨테이너 radius 제거**

아래 규칙에서 `border-radius` 값을 `0`으로 변경:

| 선택자 | 현재 값 | 변경 후 |
|--------|---------|---------|
| `.project-card` | `8px` | `0` |
| `.gh-repo-card` | `8px` | `0` |
| `.graph-container` | `8px` | `0` |
| `.post-content pre` | `6px` | `0` |
| `.post-content img` | `6px` | `0` |
| `.post-content .video-container` | `6px` | `0` |
| `.search-bar input` | `6px` | `0` |
| `.view-toggle` | `6px` | `0` |
| `.sidebar-btn::after` (tooltip) | `4px` | `0` |

- [ ] **Step 2: 스크롤바 thumb radius 제거**

```css
/* 두 곳 모두 */
.project-scroll::-webkit-scrollbar-thumb { border-radius: 2px; }
.gh-repo-scroll::-webkit-scrollbar-thumb { border-radius: 2px; }
```
→ `border-radius: 0;`

- [ ] **Step 3: zoom-preset 유지 확인**

`.zoom-preset { border-radius: 50%; }` — 원형 버튼이므로 **그대로 유지**.

- [ ] **Step 4: toggle checkbox radius 처리**

`.toggle-label input[type="checkbox"]` 의 `border-radius: 10px` → `0`
`.toggle-label input[type="checkbox"]::after` 의 `border-radius: 50%` → 슬라이더 동그라미이므로 **유지**.

- [ ] **Step 5: 시각 확인**

`http://localhost:8080/` → 프로젝트 카드, 검색창, 뷰 토글 버튼이 직각인지 확인.

- [ ] **Step 6: 커밋**

```bash
git add style.css
git commit -m "style: border-radius → 0 throughout"
```

---

## Task 4: blog/index.html — tag-filter → tag--filter

**Files:**
- Modify: `blog/index.html`

- [ ] **Step 1: JS 내 className 할당 5곳 교체**

`blog/index.html` 인라인 스크립트에서:

| 현재 | 변경 후 |
|------|---------|
| `allChip.className = 'tag-filter active'` | `allChip.className = 'tag--filter active'` |
| `document.querySelectorAll('.tag-filter:not([data-all])')` (2곳) | `document.querySelectorAll('.tag--filter:not([data-all])')` |
| `chip.className = 'tag-filter'` | `chip.className = 'tag--filter'` |
| `document.querySelectorAll('.tag-filter:not([data-all]).active')` | `document.querySelectorAll('.tag--filter:not([data-all]).active')` |

- [ ] **Step 2: 사이드바 panel-header 교체**

```html
<div class="panel-header">About</div>
```
→
```html
<div class="label">About</div>
```

- [ ] **Step 3: 변경 확인**

```bash
grep -n 'tag-filter\|panel-header' blog/index.html
```

Expected: 출력 없음.

- [ ] **Step 4: 시각 확인**

`http://localhost:8080/blog/` → 필터 칩이 outline 스타일로 보이고, 클릭 시 파랑 border로 활성화되는지 확인.

- [ ] **Step 5: 커밋**

```bash
git add blog/index.html
git commit -m "fix: blog tag-filter → tag--filter, panel-header → label"
```

---

## Task 5: index.html — 클래스명 교체

**Files:**
- Modify: `index.html`

- [ ] **Step 1: panel-header → label**

```html
<div class="panel-header">About</div>
```
→
```html
<div class="label">About</div>
```

- [ ] **Step 2: editorial-label → label--slash**

```html
<span class="editorial-label">About</span>
```
→
```html
<span class="label--slash">About</span>
```

- [ ] **Step 3: 변경 확인**

```bash
grep -n 'editorial-label\|panel-header\|section-label' index.html
```

Expected: 출력 없음.

- [ ] **Step 4: 커밋**

```bash
git add index.html
git commit -m "fix: index.html label classes → unified"
```

---

## Task 6: github/index.html — 클래스명 교체

**Files:**
- Modify: `github/index.html`

- [ ] **Step 1: panel-header → label (사이드바)**

```html
<div class="panel-header">About</div>
```
→
```html
<div class="label">About</div>
```

- [ ] **Step 2: editorial-label → label--slash (정적 헤더)**

```html
<span class="editorial-label">GitHub</span>
```
→
```html
<span class="label--slash">GitHub</span>
```

- [ ] **Step 3: JS renderSection — gh-source-label → label, h2 → div**

`github/index.html` 인라인 스크립트의 `renderSection` 함수 (~line 179):

```js
// 현재
var label = document.createElement('h2');
label.className = 'gh-source-label';
```
→
```js
// 변경 후 (h2 → div: Pico.css 헤딩 스타일 충돌 방지)
var label = document.createElement('div');
label.className = 'label';
```

- [ ] **Step 4: 변경 확인**

```bash
grep -n 'editorial-label\|panel-header\|gh-source-label' github/index.html
```

Expected: 출력 없음.

- [ ] **Step 5: 커밋**

```bash
git add github/index.html
git commit -m "fix: github/index.html label classes → unified, h2 → div"
```

---

## Task 7: posts/_template/index.html — 클래스명 교체

**Files:**
- Modify: `posts/_template/index.html`

- [ ] **Step 1: panel-header → label**

```html
<div class="panel-header">About</div>
```
→
```html
<div class="label">About</div>
```

- [ ] **Step 2: section-label → label**

```html
<div class="section-label">Related Posts</div>
```
→
```html
<div class="label">Related Posts</div>
```

- [ ] **Step 3: 변경 확인**

```bash
grep -n 'panel-header\|section-label' posts/_template/index.html
```

Expected: 출력 없음.

- [ ] **Step 4: 커밋**

```bash
git add posts/_template/index.html
git commit -m "fix: post template label classes → unified"
```

---

## Task 8: 기존 포스트 파일 일괄 교체 (8개)

**Files:**
- Modify: `posts/docker-container/index.html`, `posts/hello-world/index.html`, `posts/opencv-basics/index.html`, `posts/python-performance/index.html`, `posts/test-post-1/index.html`, `posts/간단ALU만들기_프로젝트/index.html`, `posts/딥러닝과_신경망/index.html`, `posts/인공신경망1/index.html`

- [ ] **Step 1: sed로 일괄 치환**

```bash
for f in posts/docker-container/index.html \
          posts/hello-world/index.html \
          posts/opencv-basics/index.html \
          posts/python-performance/index.html \
          posts/test-post-1/index.html \
          "posts/간단ALU만들기_프로젝트/index.html" \
          "posts/딥러닝과_신경망/index.html" \
          "posts/인공신경망1/index.html"; do
  sed -i 's/class="panel-header"/class="label"/g' "$f"
  sed -i 's/class="section-label"/class="label"/g' "$f"
done
```

- [ ] **Step 2: 치환 결과 검증**

```bash
grep -rn 'panel-header\|section-label' posts/
```

Expected: 출력 없음.

- [ ] **Step 3: 커밋**

```bash
git add posts/
git commit -m "fix: all post files label classes → unified"
```

---

## Task 9: 최종 검증

- [ ] **Step 1: 구 클래스명 잔재 전수 검사**

```bash
grep -rn 'section-label\|editorial-label\|panel-header\|gh-source-label\|tag-filter[^-]' \
  --include="*.html" --include="*.js" --include="*.css" .
```

Expected: 출력 없음 (`.superpowers/` 디렉터리 제외).

- [ ] **Step 2: border-radius 잔재 검사**

```bash
grep -n 'border-radius' style.css
```

Expected: `50%` (zoom-preset, checkbox knob) 외 모두 `0` 또는 `0px`.

- [ ] **Step 3: 전 페이지 시각 확인 체크리스트**

서버 실행 후 각 페이지 확인:

```bash
python3 -m http.server 8080
```

| 페이지 | 확인 항목 |
|--------|-----------|
| `http://localhost:8080/` | 랜딩 graph, About 섹션 `/About` slash label + 빨간 `\|`, 프로젝트 카드 직각 |
| `http://localhost:8080/blog/` | `[bracket]` 태그, outline 필터 칩, 활성 시 파랑 border |
| `http://localhost:8080/github/` | `/GitHub` slash label + 빨간 `\|`, 레포 카드 직각 |
| 포스트 페이지 | `Related Posts` 레이블 (회색+마젠타 밑줄), 포스트 태그 bracket |

- [ ] **Step 4: 최종 커밋 (필요 시)**

잔여 수정 사항이 있으면 수정 후:

```bash
git add -p
git commit -m "fix: design system cleanup"
```
