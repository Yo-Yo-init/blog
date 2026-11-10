# Personal Blog & Documentation Site — Design Specifications

> A minimal, Notion/Obsidian-inspired personal blog and documentation site. Content is authored in Markdown and rendered statically into clean, typographic pages. The design goal: neutral, quiet, content-first — like a well-organized notes app.

---

## 1. Design Language

### Palette — near-monochrome, one restrained accent

| Token             | Light Mode   | Dark Mode   | Used for                          |
| ----------------- | ------------ | ----------- | --------------------------------- |
| `--bg`            | `#ffffff`    | `#1e1e1e`   | Page background                   |
| `--bg-secondary`  | `#f7f7f5`    | `#202020`   | Panels, tags, hover fills         |
| `--text`          | `#37352f`    | `#d4d4d4`   | Body ink (Notion-style)           |
| `--text-muted`    | `#787774`    | `#9b9b9b`   | Dates, labels, secondary text     |
| `--border`        | `#e9e9e7`    | `#2f2f2f`   | Hairline borders and dividers     |
| `--border-strong` | `#d3d1cb`    | `#454545`   | Hover borders, blockquote rule    |
| `--accent`        | `#2383e2`    | `#529cca`   | Links, active filter, progress bar |
| `--accent-hover`  | `#1a6fc4`    | `#6db3dd`   | Accent hover state                |

> Neutral light/dark pair modeled on Notion's light theme and Obsidian's dark theme. A single muted blue is the only accent color; it appears only on links, the active filter pill, the active docs-sidebar item, and the reading-progress bar. The former terracotta/sage multi-accent system and per-category colors are gone. Code blocks use neutral, GitHub-like syntax colors in both themes.

### Typography

- **Everything**: system font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, …`) — no external font requests (the Google Fonts / Inter + JetBrains Mono links were removed).
- **Headings**: weight **600**, slightly tightened letter-spacing.
- **Body**: weight 400, **line-height 1.6**.
- **Code**: `ui-monospace` stack, slightly reduced size.
- **Scale**: modest fixed sizes (h1 1.875rem → h4 1rem) instead of large fluid clamps.

### Spacing & Layout

- Max content width: **700px** (prose-optimized); post pages widen to 980px for the table-of-contents column, docs pages to 920px for the sidebar.
- Flat surfaces: **hairline 1px borders**, corner radius ≤ **6px**, **no box shadows**, no gradients.
- Responsive: single-column on mobile, mobile-first.

### Interactions

- Minimal transitions: color/background changes (`150ms ease`). Link underlines appear on hover.
- Dark/light toggle (header), preference saved to `localStorage`, respects `prefers-color-scheme` on first visit.
- Reading-progress bar (accent) at the top of post pages.

---

## 2. Technical Stack

### Core Framework

| Tool | Purpose |
| ---- | ------- |
| FastAPI (`app/`, dev server) | Application server & routing |
| `build.py` (static generator) | Renders every route to `dist/` for Cloudflare Workers hosting |
| [Jinja2](https://jinja.palletsprojects.com/) | HTML templating with inheritance |

### Content Pipeline

| Library | Purpose |
| ------- | ------- |
| [python-frontmatter](https://python-frontmatter.readthedocs.io/) | Parse YAML metadata from `.md` files |
| [mistune](https://mistune.readthedocs.io/) (v3) | Fast Markdown → HTML renderer |
| [Pygments](https://pygments.org/) | Server-side syntax highlighting |

### Frontend (Minimal)

| Tool | Purpose |
| ---- | ------- |
| Vanilla CSS (custom properties) | Styling — no framework |
| Vanilla JS | Dark mode toggle + `localStorage`; client-side blog filtering (`filter.js`) |
| System fonts | Typography — zero external font requests |

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
│   │   └── YYYY-MM-DD-slug.md
│   └── docs/
│       └── getting-started.md
│
├── static/
│   ├── css/
│   │   └── style.css           # Single stylesheet, CSS variables
│   ├── js/
│   │   ├── theme.js            # Dark mode toggle
│   │   └── filter.js           # Client-side ?q= / ?category= filtering
│   └── images/
│
├── templates/
│   ├── base.html               # Shell: <head>, header nav, footer
│   ├── index.html              # Landing page (bio + latest posts)
│   ├── blog_list.html          # Blog index with filter pills
│   ├── blog_post.html          # Single post with ToC sidebar
│   ├── doc_page.html           # Doc page with sidebar nav
│   ├── about.html              # About page
│   └── 404.html                # Not-found page
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, routes, startup
│   ├── content.py              # Markdown loading, parsing, caching
│   └── config.py               # Site metadata, categories, settings
│
├── build.py                    # Static build → dist/
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
category: homelab        # only categories that actually have posts
draft: false             # true = excluded from the build
---

Your content here. Standard Markdown with fenced code blocks.
```

- **Sorting**: Blog posts ordered by `date` (newest first).
- **Drafts**: Posts with `draft: true` are hidden in production.
- **Slugs**: Derived from filename (`2025-01-15-hello-world.md` → `/blog/hello-world`).

---

## 5. Routes

| Route          | View             | Description                            |
| -------------- | ---------------- | -------------------------------------- |
| `/`            | `index.html`     | Landing — bio, latest posts            |
| `/blog`        | `blog_list.html` | Chronological post list + filter pills |
| `/blog/{slug}` | `blog_post.html` | Individual post with ToC               |
| `/docs`        | `doc_page.html`  | Documentation index / overview         |
| `/docs/{slug}` | `doc_page.html`  | Individual doc page                    |
| `/about`       | `about.html`     | About page with social links           |
| (404)          | `404.html`       | Not-found page                         |

Search (`/blog?q=…`) and category filtering (`/blog?category=…`) are handled client-side by `static/js/filter.js`.

---

## 6. What Was Removed (and Why)

- **Header search bar + ⌘K hint** — it was a plain form link to `/blog`, not real search; the tag filter pills on `/blog` cover findability. The ⌘K handler in `theme.js` was removed with it.
- **Homepage category tiles (bento grid)** — three of the four categories (`retro-gaming`, `certs`, `musings`) had zero posts and rendered as "Coming soon" placeholders. The homepage now goes straight from the bio to the latest-posts list; category filtering still works via `/blog?category=…`.
- **"Recently added" strip** — duplicated the "Latest Posts" list directly below it.
- **Homepage "Explore Topics" sidebar and "Connect" block** — tag filtering already lives on `/blog` as filter pills; social links already live on the About page and footer. The homepage is now a single centered column.
- **Back-to-top floating button** — decorative floating control with a shadow; removed for the flat aesthetic (browser shortcuts and the sticky header cover navigation).
- **Footer social icons (GitHub/LinkedIn/YouTube SVGs)** — replaced with quiet text links; the About page keeps the icon links.
- **External font requests** — system font stack instead of Google Fonts.
- **`templates/_icons.html`** — only used by the removed category tiles; deleted.

## 7. Design Principles (Summary)

1. **Content over chrome** — no visual noise, no decorative color.
2. **Near-monochrome** — neutral paper/ink tones, one restrained blue accent used sparingly.
3. **Flat** — hairline borders, ≤6px radii, zero shadows.
4. **Fast** — system fonts, server-rendered static HTML, minimal JS, no framework bloat.
5. **Simple to maintain** — small codebase, few dependencies, easy to extend.
