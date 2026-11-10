# Personal Blog & Documentation Site — Design Specifications

> A modern, minimal personal blog and documentation website built with a Python backend. Content is authored in Markdown and rendered server-side into clean, typographic pages.

---

## 1. Design Language

### Palette

| Token                | Light Mode | Dark Mode  |
| -------------------- | ---------- | ---------- |
| `--bg`                | `#faf5ee`  | `#1c1712`  |
| `--bg-secondary`      | `#f1e6d8`  | `#262019`  |
| `--text`              | `#2b2420`  | `#f0e6d8`  |
| `--text-muted`        | `#8a7a68`  | `#a8987f`  |
| `--border`            | `#e4d5c1`  | `#3b3226`  |
| `--accent` (terracotta) | `#b5502e`  | `#e08a5b`  |
| `--accent-secondary` (sage) | `#6e7f5c`  | `#8fa379`  |

> Warm, earthy minimalism. A restrained two-color accent system — terracotta and sage — against warm neutral paper and ink tones. Color is used sparingly and consistently, never decoratively; the content is still the decoration.

### Typography

- **Headings**: `Inter` (sans-serif), weight 600–700.
- **Body**: `Inter` or `system-ui`, weight 400, line-height 1.7.
- **Code**: `JetBrains Mono` or `monospace`, slightly reduced size.
- **Scale**: Modular scale with `clamp()` for fluid sizing.

### Spacing & Layout

- Max content width: `680px` (prose-optimized).
- Generous whitespace — `1.5rem` to `3rem` between sections.
- Flat design: no shadows, no rounded corners larger than `4px`, no gradients.
- Responsive: single-column, mobile-first.

### Interactions

- Minimal transitions: opacity and color on links/buttons (`150ms ease`).
- Dark/light mode toggle, preference saved to `localStorage`, respects `prefers-color-scheme` on first visit.

---

## 2. Technical Stack

### Core Framework

| Tool                                                             | Purpose                          |
| ---------------------------------------------------------------- | -------------------------------- |
| [FastAPI](https://fastapi.tiangolo.com/)                         | Application server & routing     |
| [Uvicorn](https://www.uvicorn.org/)                              | ASGI server (runs FastAPI)       |
| [Jinja2](https://jinja.palletsprojects.com/)                     | HTML templating with inheritance |

### Content Pipeline

| Library                                                                       | Purpose                                  |
| ----------------------------------------------------------------------------- | ---------------------------------------- |
| [python-frontmatter](https://python-frontmatter.readthedocs.io/)              | Parse YAML metadata from `.md` files     |
| [mistune](https://mistune.readthedocs.io/) (v3)                               | Fast Markdown → HTML renderer            |
| [Pygments](https://pygments.org/)                                             | Server-side syntax highlighting          |

### Frontend (Minimal)

| Tool                                           | Purpose                                |
| ---------------------------------------------- | -------------------------------------- |
| Vanilla CSS (custom properties)                | Styling — no framework                 |
| Vanilla JS (~20 lines)                         | Dark mode toggle + `localStorage`      |
| [Google Fonts — Inter](https://fonts.google.com/specimen/Inter) | Typography                  |

### Development

| Tool             | Purpose                                 |
| ---------------- | --------------------------------------- |
| `venv`           | Python virtual environment              |
| `watchfiles`     | Auto-reload during development          |

### `requirements.txt`

```
fastapi>=0.115
uvicorn[standard]>=0.34
jinja2>=3.1
python-frontmatter>=1.1
mistune>=3.0
pygments>=2.18
watchfiles>=1.0
```

---

## 3. Project Structure

```
blog/
├── content/                    # All authored content lives here
│   ├── blog/
│   │   └── 2025-01-15-hello-world.md
│   └── docs/
│       └── getting-started.md
│
├── static/
│   ├── css/
│   │   └── style.css           # Single stylesheet, CSS variables
│   ├── js/
│   │   └── theme.js            # Dark mode toggle (~20 lines)
│   └── images/
│
├── templates/
│   ├── base.html               # Shell: <head>, nav, footer
│   ├── index.html              # Landing page
│   ├── blog_list.html          # Blog index
│   ├── blog_post.html          # Single post
│   ├── doc_page.html           # Single doc page
│   └── doc_sidebar.html        # Partial: sidebar nav for docs
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, routes, startup
│   ├── content.py              # Markdown loading, parsing, caching
│   └── config.py               # Site metadata & settings
│
├── requirements.txt
└── design_specs.md             # ← This file
```

---

## 4. Content Format

Each Markdown file uses YAML frontmatter:

```markdown
---
title: Hello World
date: 2025-01-15
summary: A short introduction to this blog.
tags: [meta, welcome]
draft: false
---

Your content here. Standard Markdown with fenced code blocks.
```

- **Sorting**: Blog posts ordered by `date` (newest first).
- **Drafts**: Posts with `draft: true` are hidden in production.
- **Slugs**: Derived from filename (e.g., `2025-01-15-hello-world.md` → `/blog/hello-world`).

---

## 5. Routes

| Route                | View             | Description                    |
| -------------------- | ---------------- | ------------------------------ |
| `/`                  | `index.html`     | Landing — name, bio, links     |
| `/blog`              | `blog_list.html` | Chronological post list        |
| `/blog/{slug}`       | `blog_post.html` | Individual post                |
| `/docs`              | `doc_page.html`  | Documentation index / overview |
| `/docs/{slug}`       | `doc_page.html`  | Individual doc page            |

---

## 6. Implementation Phases

### Phase 1 — Foundation
1. Create `venv`, install dependencies.
2. Build `app/main.py` with FastAPI: static file mounting, Jinja2 templates, basic routes.
3. Build `app/content.py`: load Markdown files, parse frontmatter, render HTML with `mistune` + `Pygments`.

### Phase 2 — Templates & Styling
1. Create `base.html` with semantic HTML5 (`<header>`, `<main>`, `<footer>`).
2. Write `style.css` using CSS custom properties for theming.
3. Build out remaining templates: list view, post view, doc view with sidebar.

### Phase 3 — Polish
1. Dark mode toggle (`theme.js`), system preference detection.
2. SEO: dynamic `<title>`, `<meta description>`, Open Graph tags.
3. Performance: cache parsed Markdown on startup, add `Cache-Control` headers for static assets.
4. Optional: RSS feed endpoint (`/feed.xml`).

---

## 7. Design Principles (Summary)

1. **Content over chrome** — no visual noise.
2. **Black and white** — monochrome palette, no accent colors.
3. **Fast** — server-rendered HTML, minimal JS, no framework bloat.
4. **Portable** — content is plain Markdown, never locked into a platform.
5. **Simple to maintain** — small codebase, few dependencies, easy to extend.
