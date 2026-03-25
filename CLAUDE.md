# ahrism-pages

GitHub Pages 포트폴리오 + 블로그. 순수 HTML/JS, 서버 없음.

## 스택

- **CSS**: Pico.css v2 (CDN, dark theme) + `style.css` (오버라이드)
- **Markdown 렌더링**: marked.js (CDN) + highlight.js (CDN)
- **데이터**: `blog/posts.json`, `blog/graph.json`, `projects.json`

## 파일 구조

```
index.html              # 랜딩 (포스트 그래프 → About 소개)
style.css               # 다크 테마 CSS 변수 + 컴포넌트
app.js                  # 공유 JS: fetchPosts / renderPostList / renderProjectCards
graph.js                # Cytoscape.js 그래프 렌더링
projects.json           # 프로젝트 카드 데이터

blog/
  index.html            # 전체 블로그 목록
  posts.json            # 포스트 메타데이터 배열 (최신순, 자동생성)
  graph.json            # 포스트 유사도 그래프 (자동생성)
  tags.json             # 정규화된 태그 목록 (자동생성)
  .tag_cache.json       # 태그 임베딩 캐시 (자동생성, gitignore)

posts/
  _template/index.html  # 새 포스트 만들 때 복사하는 템플릿
  <slug>/
    index.html          # 템플릿 복사본
    content.md          # YAML frontmatter + 글 내용
    images/             # 이미지 (선택)

scripts/
  post_update.py        # 통합 빌드: posts.json + graph.json + tags (오케스트레이터)
  posts_list_update.py  # 포스트 스캔 · frontmatter 파싱 · posts.json 업데이트
  build_graph.py        # 임베딩 · TF-IDF · graph.json 생성 (캐시 지원)
  auto_tag.py           # 태그 추천 + 생성 + 임베딩 캐시 관리
  test_build_graph.py   # 그래프 빌드 테스트
```

## 새 포스트 추가

1. 폴더 + 템플릿 생성:
```bash
mkdir -p posts/<slug>/images
cp posts/_template/index.html posts/<slug>/index.html
```

2. `posts/<slug>/content.md` 작성 (YAML frontmatter 필수):
```markdown
---
title: "제목"
date: YYYY-MM-DD
tags: [tag1, tag2]  # 선택사항: 없으면 자동 추천
summary: "한 줄 요약 (없으면 본문에서 자동 추출)"
---

본문 내용...
```

3. 빌드:
```bash
cd scripts && uv run python post_update.py
```

| 옵션 | 설명 |
|------|------|
| (없음) | 증분 업데이트 — 바뀐 글만 임베딩 재계산 + 태그 레지스트리 갱신 |
| `--posts-only` | posts.json만 업데이트 (ML 모델 로딩 없음) |
| `--force` | 캐시 무시, 전체 임베딩 재계산 |

## 색상 시스템

| 역할 | 값 |
|------|-----|
| 배경 | `#0a0a0a` |
| 카드 | `#111111` |
| 테두리 | `#1e1e1e` |
| Primary (magenta) | `#dc00c9` |
| Secondary (blue) | `#4a62ff` |
| Critical (red) | `#ff0000` |
| 본문 | `#cccccc` |
| 흐린 텍스트 | `#555555` |

## 로컬 미리보기

```bash
python3 -m http.server 8080
# http://localhost:8080/
```

fetch() 때문에 file:// 직접 열기 불가 — 반드시 서버 필요.
