# ahrism-pages: Portfolio & Blog Site Design

## Context

GitHub Pages 기반 개인 포트폴리오 + 블로그 사이트. 프레임워크 없이 순수 HTML/JS/CSS만 사용하며, 코드 구조가 직관적이어서 수정이 쉬워야 한다. 블로그 글은 Markdown으로 작성하고, 각 글마다 독립 폴더를 가진다.

## Design Decisions

| 항목 | 결정 |
|------|------|
| 구조 | 멀티 페이지 |
| 스타일 | 다크 미니멀, AI 느낌 배제, 그라데이션 없음 |
| 컬러 | 주 강조 `#dc00c9`, 보조 `#4a62ff`, 최강조 `#ff0000` |
| 언어 | UI/네비 영어, 콘텐츠 한국어/혼합 |
| 포트폴리오 섹션 | About, Projects, Blog (최신 글) |
| 블로그 렌더링 | 하이브리드 — 각 폴더에 index.html 템플릿 + content.md |
| MD 파서 | marked.js (CDN) |
| CSS 베이스 | Pico.css (CDN) — classless, 다크 모드 내장. 커스텀 오버라이드만 `style.css`에 작성 |
| 경로 전략 | 모든 경로를 상대 경로로 처리. GitHub Pages 프로젝트 사이트 호환 |
| 반응형 | Pico.css 내장 반응형 + 필요시 커스텀 미디어쿼리 보완 |

## File Structure

```
ahrism-pages/
├─ index.html              # 메인 (About + Projects + Recent Posts)
├─ style.css               # 커스텀 오버라이드 (컬러, 레이아웃 미세 조정만)
├─ app.js                  # 공용 JS (네비게이션, 유틸리티)
├─ blog/
│  ├─ index.html           # 블로그 전체 목록 페이지
│  └─ posts.json           # 글 메타데이터 인덱스
├─ posts/
│  ├─ _template/
│  │  └─ index.html        # 포스트 템플릿 원본 (posts.json에 등록하지 않음)
│  ├─ my-first-post/
│  │  ├─ index.html        # _template/index.html 복사본
│  │  ├─ content.md        # 마크다운 글
│  │  └─ images/           # 첨부 이미지
│  └─ second-post/
│     ├─ index.html
│     ├─ content.md
│     └─ images/
└─ assets/                 # 프로필 이미지, 아이콘 등
```

## Asset Path Strategy

모든 페이지에서 상대 경로를 사용한다. GitHub Pages 프로젝트 사이트(`username.github.io/repo-name/`)에서도 동작하도록 절대 경로(`/style.css`)를 사용하지 않는다.

| 페이지 위치 | CSS/JS 참조 | posts.json 참조 |
|-------------|------------|----------------|
| `index.html` | `./style.css`, `./app.js` | `./blog/posts.json` |
| `blog/index.html` | `../style.css`, `../app.js` | `./posts.json` |
| `posts/{slug}/index.html` | `../../style.css`, `../../app.js` | `../../blog/posts.json` |

## Pages

### 1. index.html — 메인 페이지

상단 네비게이션 + 3개 섹션으로 구성된 단일 스크롤 페이지.

**Navigation:**
- 로고 "ahrism" (좌측)
- About / Projects / Blog 링크 (우측)
- 현재 활성 섹션은 마젠타(`#dc00c9`)로 표시
- Blog 링크는 `./blog/index.html`로 이동

**About 섹션:**
- 이름, 한 줄 소개
- 짧은 자기소개 텍스트
- 기술 태그 (인디고 블루 배경)

**Projects 섹션:**
- 프로젝트 카드 그리드 (2열)
- 각 카드: 이름, 설명, 태그, GitHub 링크
- 프로젝트 데이터는 index.html 안에 직접 작성 (별도 JSON 불필요)

**Recent Posts 섹션:**
- `blog/posts.json`에서 최신 3개 글을 fetch해서 표시
- 글 제목, 날짜, 태그
- "View All →" 링크 → blog/index.html


### 3. posts/{slug}/index.html — 블로그 글 페이지

`posts/_template/index.html`의 복사본. 모든 포스트가 동일한 HTML 구조를 가진다.

- 같은 네비게이션
- "← Back to Blog" 링크
- JS가 `../../blog/posts.json`을 fetch하고, 현재 URL 경로에서 slug를 추출하여 매칭 → 제목/날짜/태그를 페이지 상단에 렌더링
- 같은 폴더의 `content.md`를 `fetch()`
- `marked.js`(CDN)로 HTML 변환 후 본문 영역에 렌더링
- 이미지는 `images/photo.png` 같은 상대 경로로 참조
- 코드 블록 스타일링: `highlight.js`(CDN)로 syntax highlighting

### 4. blog/index.html — 블로그 목록 상세

- 같은 네비게이션
- `posts.json`에서 전체 글 목록 fetch → 배열 순서대로 렌더링 (JSON 파일을 newest-first로 유지)
- 각 항목: 제목, 날짜, 태그, 요약
- 리스트 형태 (카드가 아닌 구분선으로 나눈 목록)
- 페이지네이션: 초기엔 불필요, 글이 많아지면 추후 추가
- 클릭 시 `../posts/{slug}/index.html`로 이동

## blog/posts.json Format

```json
[
  {
    "slug": "my-first-post",
    "title": "글 제목",
    "date": "2024-03-15",
    "tags": ["python", "edge-ai"],
    "summary": "짧은 요약 한 줄"
  }
]
```

## Color System

| 색상 | 코드 | 용도 |
|------|------|------|
| 마젠타 | `#dc00c9` | 주 강조 — 로고 이름, 활성 네비, 호버, 섹션 라벨 |
| 인디고 블루 | `#4a62ff` | 보조 강조 — 링크, 태그 배경, 메타 정보 |
| 레드 | `#ff0000` | 최강조 — CTA 버튼, 핵심 배지 (극소량) |
| 배경 | `#0a0a0a` | 페이지 배경 |
| 카드 배경 | `#111111` | 카드, 코드 블록 배경 |
| 테두리 | `#1e1e1e` | 카드 보더, 구분선 |
| 본문 텍스트 | `#cccccc` | 일반 텍스트 |
| 보조 텍스트 | `#555555` | 날짜, 설명 등 |

## Typography

Pico.css 기본 폰트 사용 (시스템 폰트 스택). 별도 폰트 로딩 없음.

## Blog Post Workflow

새 글 추가 순서:

1. `posts/new-slug/` 폴더 생성
2. `posts/_template/index.html`을 복사
3. `content.md` 작성 (이미지는 `images/` 폴더에)
4. `blog/posts.json` 배열 맨 앞에 메타데이터 추가 (newest-first 유지)
5. git push

## Responsive Design

Pico.css의 내장 반응형을 기본으로 사용. 프로젝트 카드 그리드만 커스텀 미디어쿼리 추가:

- **768px 이상**: 프로젝트 카드 2열
- **768px 미만**: 프로젝트 카드 1열 스택
- 네비게이션, 블로그 목록/글 페이지는 Pico.css 기본 반응형으로 충분

## Dependencies

- `Pico.css` — CDN, classless CSS 베이스 (`https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css`)
- `marked.js` — CDN, Markdown → HTML 변환 (`https://cdn.jsdelivr.net/npm/marked/marked.min.js`)
- `highlight.js` — CDN, 코드 syntax highlighting (`https://cdn.jsdelivr.net/gh/highlightjs/cdn-release/build/highlight.min.js`)
- 그 외 외부 의존성 없음

## Verification

1. `index.html`을 브라우저에서 열어 3개 섹션이 정상 표시되는지 확인
2. `blog/index.html`에서 `posts.json`의 글 목록이 렌더링되는지 확인
3. 포스트 `index.html`에서 `content.md`가 정상 렌더링되는지 확인
4. 이미지 상대 경로가 정상 작동하는지 확인
5. 네비게이션 링크가 모든 페이지에서 동작하는지 확인
6. GitHub Pages에 push 후 실제 URL에서 전체 사이트 확인
