# ahrism-pages Portfolio & Blog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a GitHub Pages portfolio + blog site using plain HTML/JS with Pico.css, dark minimal theme, and Markdown blog posts.

**Architecture:** Multi-page static site. Pico.css (CDN) for base styling, custom CSS overrides for dark theme colors. Blog posts stored as Markdown in individual folders, rendered client-side with marked.js. Post metadata in blog/posts.json.

**Tech Stack:** HTML, JS, Pico.css (CDN), marked.js (CDN), highlight.js (CDN)

**Spec:** `docs/superpowers/specs/2026-03-23-portfolio-blog-design.md`

---

## File Map

| File | Responsibility |
|------|---------------|
| `style.css` | Pico.css dark theme color overrides, project card grid, custom component styles |
| `app.js` | Shared JS: posts.json fetcher, post list renderer, slug extractor |
| `index.html` | Main page: nav + About + Projects + Recent Posts |
| `blog/index.html` | Full blog list page |
| `blog/posts.json` | Blog post metadata index (newest-first) |
| `posts/_template/index.html` | Canonical post template (copy for each new post) |
| `posts/hello-world/content.md` | Sample blog post |
| `posts/hello-world/index.html` | Template copy for sample post |

---

### Task 1: Custom CSS — style.css

**Files:**
- Create: `style.css`

- [x] **Step 1: Create style.css with Pico.css dark theme overrides**

Override Pico.css CSS custom properties for the dark color scheme. Add project card grid and tag styles.

```css
/* Pico.css dark theme color overrides */
:root {
  --pico-background-color: #0a0a0a;
  --pico-card-background-color: #111111;
  --pico-card-border-color: #1e1e1e;
  --pico-primary: #dc00c9;
  --pico-primary-hover: #b800a8;
  --pico-secondary: #4a62ff;
  --pico-secondary-hover: #3a50dd;
  --pico-color: #cccccc;
  --pico-muted-color: #555555;
  --pico-border-color: #1e1e1e;
}

/* Accent colors */
.accent-primary { color: #dc00c9; }
.accent-secondary { color: #4a62ff; }
.accent-critical { color: #ff0000; }

/* Section labels */
.section-label {
  font-size: 0.7rem;
  color: #dc00c9;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 1rem;
}

/* Tag chips */
.tag {
  display: inline-block;
  font-size: 0.75rem;
  color: #4a62ff;
  background: rgba(74, 98, 255, 0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
}

/* Project cards grid */
.project-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}
@media (max-width: 768px) {
  .project-grid {
    grid-template-columns: 1fr;
  }
}

/* Project card */
.project-card {
  background: #111;
  border: 1px solid #1e1e1e;
  border-radius: 8px;
  padding: 1.2rem;
}
.project-card h3 { margin-bottom: 0.3rem; font-size: 1rem; }
.project-card p { color: #555; font-size: 0.85rem; margin-bottom: 0.8rem; }

/* Blog post list item */
.post-item {
  padding: 0.8rem 0;
  border-bottom: 1px solid #111;
}
.post-item h3 { margin-bottom: 0.2rem; font-size: 1rem; }
.post-meta { font-size: 0.8rem; color: #555; }

/* Post content area */
.post-content img {
  max-width: 100%;
  border-radius: 6px;
}
.post-content pre {
  background: #111;
  border: 1px solid #1e1e1e;
  border-radius: 6px;
}

/* CTA button (critical accent) */
.btn-critical {
  background: #ff0000;
  color: #fff;
  border: none;
}

/* Nav active link */
nav a.active { color: #dc00c9; }
```

- [x] **Step 2: Commit**

```bash
git add style.css
git commit -m "feat: add custom CSS overrides for dark theme"
```

---

### Task 2: Shared JavaScript — app.js

**Files:**
- Create: `app.js`

- [ ] **Step 1: Create app.js with shared utilities**

Three functions: fetch posts, render post list, extract slug from URL.

```js
// Fetch posts.json from a relative path and return parsed array
async function fetchPosts(jsonPath) {
  const res = await fetch(jsonPath);
  if (!res.ok) return [];
  return res.json();
}

// Render a list of posts into a container element
// Each post: { slug, title, date, tags, summary }
// postsBasePath: relative path prefix to posts/ directory
function renderPostList(posts, container, postsBasePath) {
  container.innerHTML = '';
  posts.forEach(post => {
    const item = document.createElement('a');
    item.href = `${postsBasePath}${post.slug}/`;
    item.className = 'post-item';
    item.style.textDecoration = 'none';
    item.style.display = 'block';
    item.innerHTML = `
      <h3>${post.title}</h3>
      <div class="post-meta">
        ${post.date}
        ${post.tags.map(t => `<span class="tag">${t}</span>`).join(' ')}
      </div>
      ${post.summary ? `<p style="color:#777;font-size:0.85rem;margin-top:0.3rem">${post.summary}</p>` : ''}
    `;
    container.appendChild(item);
  });
}

// Extract slug from current URL path
// e.g., /repo/posts/my-post/ → "my-post"
// e.g., /repo/posts/my-post/index.html → "my-post"
function getSlugFromURL() {
  const path = window.location.pathname.replace(/\/index\.html$/, '').replace(/\/$/, '');
  const parts = path.split('/');
  return parts[parts.length - 1];
}
```

- [ ] **Step 2: Commit**

```bash
git add app.js
git commit -m "feat: add shared JS utilities for blog"
```

---

### Task 3: Main Page — index.html

**Files:**
- Create: `index.html`
- Create: `assets/` directory

- [ ] **Step 1: Create index.html with nav + About + Projects + Recent Posts**

Full HTML page loading Pico.css (CDN, dark), custom style.css, and app.js. About/Projects content hardcoded. Recent Posts section fetches from blog/posts.json dynamically.

Key structure:
```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ahrism</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <header class="container">
    <nav>
      <ul><li><strong><a href="./">ahrism</a></strong></li></ul>
      <ul>
        <li><a href="#about" class="active">About</a></li>
        <li><a href="#projects">Projects</a></li>
        <li><a href="./blog/">Blog</a></li>
      </ul>
    </nav>
  </header>
  <main class="container">
    <!-- About section -->
    <section id="about">
      <div class="section-label">About</div>
      <h1>ahrism</h1>
      <p>Building Practical Systems.</p>
      <p>알고리즘을 밑바닥부터 이해하고, 소프트웨어 지능과 현실 세계의 접점을 만듭니다.</p>
      <div>
        <span class="tag">Python</span>
        <span class="tag">C++</span>
        <span class="tag">PyTorch</span>
        <span class="tag">OpenCV</span>
        <span class="tag">Linux</span>
        <span class="tag">Docker</span>
      </div>
    </section>

    <!-- Projects section -->
    <section id="projects">
      <div class="section-label">Projects</div>
      <div class="project-grid">
        <article class="project-card">
          <h3>Project Name</h3>
          <p>프로젝트 설명</p>
          <div><span class="tag">tag</span></div>
        </article>
      </div>
    </section>

    <!-- Recent Posts section -->
    <section id="recent-posts">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div class="section-label">Recent Posts</div>
        <a href="./blog/" class="accent-secondary" style="font-size:0.85rem">View All →</a>
      </div>
      <div id="posts-container"></div>
    </section>
  </main>

  <footer class="container">
    <small>&copy; 2024 ahrism</small>
  </footer>

  <script src="./app.js"></script>
  <script>
    fetchPosts('./blog/posts.json').then(posts => {
      const container = document.getElementById('posts-container');
      renderPostList(posts.slice(0, 3), container, './posts/');
    });
  </script>
</body>
</html>
```

- [ ] **Step 2: Create assets/ directory**

```bash
mkdir -p assets
```

- [ ] **Step 3: Verify in browser**

Open `index.html` in browser. Confirm:
- Dark background (#0a0a0a)
- Nav shows "ahrism" + links
- About section with tags
- Projects section with card grid
- Recent Posts section (empty until posts.json exists)

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add main page with About, Projects, Recent Posts"
```

---

### Task 4: Blog Posts Data — blog/posts.json

**Files:**
- Create: `blog/posts.json`

- [ ] **Step 1: Create blog/ directory and posts.json with sample entry**

```json
[
  {
    "slug": "hello-world",
    "title": "Hello World — 첫 번째 글",
    "date": "2026-03-23",
    "tags": ["blog"],
    "summary": "ahrism 블로그의 첫 번째 글입니다."
  }
]
```

- [ ] **Step 2: Commit**

```bash
git add blog/posts.json
git commit -m "feat: add blog posts.json with sample entry"
```

---

### Task 5: Blog List Page — blog/index.html

**Files:**
- Create: `blog/index.html`

- [ ] **Step 1: Create blog/index.html**

Same structure as main page but with full blog list. Loads `posts.json` (relative: `./posts.json`) and renders all entries.

Key structure:
```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog — ahrism</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <header class="container">
    <nav>
      <ul><li><strong><a href="../">ahrism</a></strong></li></ul>
      <ul>
        <li><a href="../#about">About</a></li>
        <li><a href="../#projects">Projects</a></li>
        <li><a href="./" class="active">Blog</a></li>
      </ul>
    </nav>
  </header>
  <main class="container">
    <h1>Blog</h1>
    <div id="posts-container"></div>
  </main>
  <footer class="container">
    <small>&copy; 2024 ahrism</small>
  </footer>
  <script src="../app.js"></script>
  <script>
    fetchPosts('./posts.json').then(posts => {
      const container = document.getElementById('posts-container');
      renderPostList(posts, container, '../posts/');
    });
  </script>
</body>
</html>
```

- [ ] **Step 2: Verify in browser**

Open `blog/index.html` via local server. Confirm:
- Nav shows Blog as active
- "Hello World" post appears in list
- Link points to `../posts/hello-world/`

- [ ] **Step 3: Commit**

```bash
git add blog/index.html
git commit -m "feat: add blog list page"
```

---

### Task 6: Post Template — posts/_template/index.html

**Files:**
- Create: `posts/_template/index.html`

- [ ] **Step 1: Create the post template**

Template fetches `../../blog/posts.json`, extracts slug from URL, displays metadata, then fetches `./content.md` and renders with marked.js + highlight.js.

Key structure:
```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Loading... — ahrism</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
  <link rel="stylesheet" href="../../style.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release/build/styles/github-dark.min.css">
</head>
<body>
  <header class="container">
    <nav>
      <ul><li><strong><a href="../../">ahrism</a></strong></li></ul>
      <ul>
        <li><a href="../../#about">About</a></li>
        <li><a href="../../#projects">Projects</a></li>
        <li><a href="../../blog/" class="active">Blog</a></li>
      </ul>
    </nav>
  </header>
  <main class="container">
    <a href="../../blog/" class="accent-secondary" style="font-size:0.85rem">← Back to Blog</a>
    <div id="post-header">
      <h1 id="post-title"></h1>
      <div class="post-meta" id="post-meta"></div>
    </div>
    <article id="post-content" class="post-content"></article>
  </main>
  <footer class="container">
    <small>&copy; 2024 ahrism</small>
  </footer>

  <script src="../../app.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release/build/highlight.min.js"></script>
  <script>
    (async () => {
      const slug = getSlugFromURL();

      // Load metadata from posts.json
      const posts = await fetchPosts('../../blog/posts.json');
      const post = posts.find(p => p.slug === slug);
      if (post) {
        document.title = `${post.title} — ahrism`;
        document.getElementById('post-title').textContent = post.title;
        document.getElementById('post-meta').innerHTML =
          `${post.date} ${post.tags.map(t => `<span class="tag">${t}</span>`).join(' ')}`;
      }

      // Load and render markdown
      const res = await fetch('./content.md');
      if (res.ok) {
        const md = await res.text();
        document.getElementById('post-content').innerHTML = marked.parse(md);
        document.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));
      } else {
        document.getElementById('post-content').innerHTML = '<p>글을 불러올 수 없습니다.</p>';
      }
    })();
  </script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add posts/_template/index.html
git commit -m "feat: add blog post template"
```

---

### Task 7: Sample Blog Post

**Files:**
- Create: `posts/hello-world/index.html` (copy from template)
- Create: `posts/hello-world/content.md`
- Create: `posts/hello-world/images/` (empty directory)

- [ ] **Step 1: Copy template to sample post**

```bash
mkdir -p posts/hello-world/images
cp posts/_template/index.html posts/hello-world/index.html
```

- [ ] **Step 2: Create sample content.md**

```markdown
블로그의 첫 번째 글입니다.

## 소개

이 블로그에서는 개발, 알고리즘, 데이터 분석 등에 대한 글을 작성합니다.

## 코드 예시

간단한 Python 코드:

```python
def hello():
    print("Hello, World!")

hello()
```

## 마무리

앞으로 다양한 글을 올리겠습니다.
```

- [ ] **Step 3: Verify in browser**

Serve locally (e.g., `python3 -m http.server`). Open `posts/hello-world/index.html`. Confirm:
- Title "Hello World — 첫 번째 글" from posts.json
- Date and tags rendered
- Markdown rendered as HTML
- Code block with syntax highlighting
- "← Back to Blog" link works

- [ ] **Step 4: Commit**

```bash
git add posts/hello-world/
git commit -m "feat: add sample hello-world blog post"
```

---

### Task 8: End-to-End Verification

- [ ] **Step 1: Start local server**

```bash
cd /home/ahris/ahrism-pages && python3 -m http.server 8080
```

- [ ] **Step 2: Verify all pages**

1. `http://localhost:8080/` — Main page: About, Projects, Recent Posts (shows "Hello World")
2. `http://localhost:8080/blog/` — Blog list shows all posts
3. `http://localhost:8080/posts/hello-world/` — Post renders markdown, code highlighted
4. All navigation links work across pages
5. Responsive: resize to mobile width, project grid becomes 1 column

- [ ] **Step 3: Clean up and final commit**

Remove any placeholder content that should be personalized. Ensure `.superpowers/` is in `.gitignore`.

```bash
echo ".superpowers/" >> .gitignore
git add .gitignore
git commit -m "chore: add .gitignore"
```
