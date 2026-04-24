# Twinkle 공간 설계

**날짜:** 2026-04-25  
**상태:** 승인됨

---

## Context

블로그 포스트는 완성도 높은 긴 글을 위한 공간이다. 그러나 실제 작업 중에는 짧은 디버깅 기록, 논문 메모, 아이디어 스케치처럼 포스트로 만들기엔 너무 가볍지만 기록할 가치는 있는 단상들이 생긴다. 트윈클 공간은 이런 경량 콘텐츠를 위한 독립 섹션이다.

---

## 파일 구조

```
twinkle/
  images/                          # 이미지 공유 폴더
  YYYY-MM-DD-slug.md               # 트윈클 1개 = .md 파일 1개
  index.html                       # 피드 + 아카이브 페이지
  twinkles.json                    # 자동생성, 커밋 포함 (posts.json과 동일)

scripts/
  twinkle_update.py                # 신규: 독립 모듈
  post_update.py                   # 수정: twinkle_update import 추가
```

### Frontmatter 스키마

```yaml
---
title: "제목"
date: YYYY-MM-DD
tags: [tag1, tag2]   # 선택사항
---
본문 (500자 이하 권장)
```

타입 필드 불필요 — `twinkle/` 디렉토리에 위치한 것 자체가 타입을 의미한다.

### twinkles.json 스키마

```json
[
  {
    "slug": "2026-04-24-batchnorm",
    "date": "2026-04-24",
    "title": "BatchNorm 위치가 결정적이었다",
    "tags": ["딥러닝", "디버깅"],
    "content": "전체 본문 (마크다운)"
  }
]
```

본문이 짧으므로 JSON에 임베드 — 추가 fetch 없이 index.html에서 바로 렌더링.

---

## 레이아웃 (twinkle/index.html)

### 데스크탑 (≥768px)

```
┌─────────────────────────────────┬──────────────────┐
│  ✦ TWINKLE                      │  ARCHIVE    ⠿    │
│                                 │  [딥러닝] [아이디어]│
│  ┌─────────────────────────┐    │  ──────────────── │
│  │ 2026-04-24 · #딥러닝    │    │  04-24 배치놈 ←현재│
│  │ BatchNorm 위치가...     │    │  04-21 sparse attn│
│  │ [펼침 상태]             │    │  03-15 flash attn │
│  └─────────────────────────┘    │  ...              │
│  ┌─────────────────────────┐    │  (세로 스크롤)     │
│  │ 2026-04-21 · #아이디어  │    │                   │
│  │ ▼ 더보기                │    │                   │
│  └─────────────────────────┘    │                   │
└─────────────────────────────────┴──────────────────┘
```

- 피드: 최신순, 카드 expand/collapse
- 아카이브: 날짜+제목 목록, 세로 스크롤 가능
- 아카이브 우측 상단 `⠿` — 드래그 핸들 (너비 조절)

### 모바일/태블릿 (<768px)

아카이브 패널 숨김, 피드만 표시.

---

## 인터랙션

### 아카이브 클릭 → 피드 재정렬

아카이브 항목 클릭 시:
1. 해당 트윈클을 피드 첫 번째 카드로 배치, 주변 앞뒤 항목을 함께 표시
2. URL을 `/twinkle/#slug`로 업데이트
3. 기준 카드에 파란 테두리로 "현재 기준점" 표시

페이지 진입 시 URL에 `#slug`가 있으면 해당 트윈클 기준으로 피드 초기화.

### 카드 expand/collapse

- 본문 ≤300자: 클릭 없이 바로 표시
- 본문 >300자: 300자까지 표시 후 `▼ 더보기` 버튼
- 펼침 상태는 `sessionStorage`에 저장 — 같은 탭 내 뒤로가기 후 복귀 시 유지

### 태그 필터

아카이브 상단 태그 칩 클릭 시:
- 피드와 아카이브 모두 해당 태그 트윈클만 필터링
- 전체 칩 클릭 시 필터 해제

---

## 빌드 파이프라인

### twinkle_update.py (신규 독립 모듈)

```
scripts/twinkle_update.py
```

역할:
1. `twinkle/*.md` 파일 스캔 (날짜순 정렬)
2. YAML frontmatter + 본문 파싱
3. `twinkle/twinkles.json` 생성/업데이트

기존 `posts_list_update.py`와 동일한 패턴. ML 모델 불필요 — 빠른 단독 실행 가능.

```bash
# 단독 실행
uv run python twinkle_update.py
```

### post_update.py 수정

```python
from twinkle_update import update_twinkles_json

# main() 마지막에 추가:
update_twinkles_json()
```

`uv run python post_update.py` 실행 시 자동으로 `twinkles.json`까지 업데이트.

---

## 사이드바 수정

다음 3개 파일의 사이드바에 ✦ Twinkle 버튼 추가:

- `index.html`
- `blog/index.html`
- `posts/_template/index.html`

```html
<button class="sidebar-btn" data-label="Twinkle" data-href="/twinkle/">✦</button>
```

---

## style.css 추가

- `.twinkle-card` — 트윈클 카드 기본 스타일 (마젠타 테두리)
- `.twinkle-card.anchor` — 아카이브 기준 선택 시 파란 테두리
- `.twinkle-archive` — 아카이브 패널
- `.twinkle-archive .tag-chip` — 태그 필터 칩
- `@media (max-width: 767px) { .twinkle-archive { display: none; } }`

---

## 수정 파일 목록

| 파일 | 작업 |
|------|------|
| `twinkle/index.html` | 신규 생성 |
| `twinkle/images/` | 신규 생성 |
| `scripts/twinkle_update.py` | 신규 생성 |
| `scripts/post_update.py` | import + 호출 추가 |
| `index.html` | 사이드바 ✦ 버튼 추가 |
| `blog/index.html` | 사이드바 ✦ 버튼 추가 |
| `posts/_template/index.html` | 사이드바 ✦ 버튼 추가 |
| `style.css` | 트윈클 카드 + 아카이브 스타일 추가 |

---

## 검증

1. 샘플 트윈클 2-3개 작성 (`twinkle/YYYY-MM-DD-slug.md`)
2. `uv run python twinkle_update.py` → `twinkle/twinkles.json` 생성 확인
3. `uv run python post_update.py` → twinkles.json도 함께 업데이트 확인
4. `python3 -m http.server 8080` 실행 후 `http://localhost:8080/twinkle/` 접속
5. 확인 항목:
   - 피드 카드 렌더링 (expand/collapse, 더보기)
   - 아카이브 패널 표시 + 태그 필터 동작
   - 아카이브 클릭 → 피드 재정렬 + URL `#slug` 업데이트
   - 모바일 뷰포트에서 아카이브 숨김
   - 사이드바 ✦ 버튼 → `/twinkle/` 이동

---

## 스코프 외 (추후 고려)

- 트윈클 노드를 메인 그래프에 포함
- 트윈클 검색 (blog 검색과 통합)
