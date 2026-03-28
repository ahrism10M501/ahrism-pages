# Landing Page UI Improvements & Mobile Bug Fixes

**Date:** 2026-03-28
**Status:** Approved for implementation

---

## Context

랜딩 페이지(`index.html`)의 시각적 단조로움 개선과 모바일 UX 버그 2건 수정. 모든 변경은 순수 HTML/JS/CSS이며 빌드 없이 적용.

---

## Feature 1: Graph Node Scale-up Highlight (13초 순환)

### 목표
Cytoscape.js 그래프 노드 중 2~3개를 13초마다 랜덤 선택하여 크게 강조. 시각적 관심 유도.

### 설계

**graph.js line 52** — 노드 `transition-property`에 `width, height` 추가:
```js
'transition-property': 'background-color, border-color, color, opacity, width, height',
```
Cytoscape 내장 transition으로 크기 변화를 부드럽게 처리 (기존 300ms 그대로 사용).

**index.html** — `if (hasGraph)` 블록 내 `initGraph()` 호출 직후에 IIFE 추가:
```js
(function () {
  var prevHighlighted = [];
  setInterval(function () {
    var cy = window.__indexCy;
    if (!cy) return;
    prevHighlighted.forEach(function (item) {
      item.node.style({ width: item.w, height: item.h });
    });
    prevHighlighted = [];
    var nodes = cy.nodes().toArray();
    var count = 2 + Math.floor(Math.random() * 2); // 2 or 3
    var picks = nodes.slice().sort(function () { return Math.random() - 0.5; }).slice(0, Math.min(count, nodes.length));
    picks.forEach(function (node) {
      var curW = parseFloat(node.style('width'));
      var curH = parseFloat(node.style('height'));
      prevHighlighted.push({ node: node, w: curW, h: curH });
      node.style({ width: curW * 1.7, height: curH * 1.7 });
    });
  }, 13000);
})();
```

**핵심 결정:**
- `node.style('width')`로 현재 크기 읽음 — `applyDepthEffect`가 degree 기반으로 노드별 크기를 다르게 설정하므로, 30px 하드코딩 대신 실제 값 기준 1.7배 스케일
- `prevHighlighted` 배열에 원본 크기를 저장해 다음 틱에 복원
- `hasGraph` 블록 안에 있으므로 폴백 모드에선 실행 안 됨

---

## Bug Fix 2: 모바일 그래프 확장 후 축소 불가

### 문제
그래프를 아래로 당겨 100vh로 확장한 후, 모바일에서 위로 스와이프해 축소하는 경로가 없음.
- `touchmove` 핸들러가 `delta <= 0` (위 스와이프)이면 즉시 `dragActive = false`로 취소
- `touchend` 핸들러에 `expanded === true` 분기 없음
- 데스크톱용 스크롤 이벤트 축소는 Cytoscape 캔버스가 터치 스크롤을 흡수해 모바일에서 동작 안 함

### 수정 (index.html 내 touch 스크립트 블록)

**touchstart** (line 177):
```js
// Before
if (window.scrollY > 2) return;
// After
if (window.scrollY > 2 && !expanded) return;
```

**touchmove** (line 185):
```js
// Before
if (delta <= 0) { dragActive = false; return; }
// After
if (delta <= 0 && !expanded) { dragActive = false; return; }
```

**touchend** (line 191) — 파라미터 `e` 추가 + `else` 분기:
```js
// Before
document.addEventListener('touchend', function () {
  ...
  if (!expanded) { ... }
}, { passive: true });

// After
document.addEventListener('touchend', function (e) {
  ...
  if (!expanded) {
    const delta = gc.offsetHeight - baseH();
    if (delta > SNAP_THRESHOLD) snapExpand();
    else snapCollapse();
  } else {
    const swipeDelta = e.changedTouches[0].clientY - startY;
    if (swipeDelta < -SNAP_THRESHOLD) snapCollapse();
  }
}, { passive: true });
```

**핵심 결정:**
- `e.changedTouches` 사용 (`touchend`에서 `e.touches`는 빈 배열)
- 80px 이상 위로 스와이프해야 축소 — 기존 확장 임계값과 대칭
- 시각적 피드백(touchmove 중 높이 줄이기) 생략 — 단순성 우선

---

## Bug Fix 3: 모바일 사이드바 Home 아이콘 가림

### 문제
`#sidebar-toggle` (`position:fixed; top:8px; left:8px; z-index:200`)이 사이드바 첫 번째 버튼(Home, `top:0`)을 덮음.

### 수정 (style.css)

`@media (max-width: 640px)` 블록(line 533) 내 닫는 `}` 직전에 추가:
```css
#sidebar .sidebar-icons {
  padding-top: 52px;
}
```

계산: toggle `top:8px` + `height:36px` + 8px gap = 52px.
데스크톱에선 `#sidebar-toggle { display:none }`이므로 영향 없음.

---

## 수정 파일 요약

| 파일 | 변경 유형 | 위치 |
|------|---------|------|
| `graph.js` | line 52 수정 | `transition-property` 확장 |
| `index.html` | line 128 이후 추가 | 노드 highlight interval IIFE |
| `index.html` | line 177, 185, 191 수정 | touch 핸들러 3곳 |
| `style.css` | line 569 이후 추가 | mobile media query padding-top |

---

## 검증

1. **노드 강조**: 13초 대기 후 2~3 노드가 부드럽게 커지는지 확인. 다음 틱에 원래 크기로 복원되는지 확인.
2. **스와이프 축소**: 모바일 뷰포트에서 그래프를 아래로 당겨 확장 → 위로 80px+ 스와이프 → 축소 확인. 80px 미만으로 스와이프 시 유지 확인.
3. **Home 아이콘**: 모바일에서 햄버거 버튼 탭 → Home ⌂ 버튼이 가려지지 않고 보이는지 확인.
