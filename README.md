# Chili Lab

Homelab, networking and self-hosted AI agent guides. Markdown content rendered with Jinja templates into a static site, hosted on Cloudflare.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py --serve      # http://localhost:8000
```

Optional live-reload server (the original FastAPI app):

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Writing

Content is Markdown with YAML front matter. Drop a `.md` file into the right folder and the build picks it up:

```
content/
├── blog/       date-prefixed posts (2025-01-15-my-post.md)
└── docs/       lab reference pages (lab-overview.md)
```

Front matter, folders, tags and publishing rules are in [BLOG.md](BLOG.md). The short version:

### Writing a blog post

Create `content/blog/YYYY-MM-DD-slug.md` with this front matter:

```yaml
---
title: "Your Post Title"
date: 2025-02-14
summary: "A short description for the blog list."
tags: [homelab, proxmox]
draft: false
---
```

Tags must exist in `content/tags.yaml`. Set `draft: true` to hide a post while you are still working on it.

### Writing a doc page

Doc pages are public reference notes about the lab and live in `content/docs/`. They must not contain internal IPs, real hostnames or domains, or credentials. The `order` field controls sidebar sorting (lower numbers first):

```yaml
---
title: "Page Title"
order: 1
---
```

## Deployment

Cloudflare builds every push:

| Setting | Value |
| --- | --- |
| Build command | `pip install -r requirements.txt && python build.py` |
| Output | `dist/` (set in `wrangler.jsonc`) |
| Production branch | `main` |
| Previews | every other branch |

`hosting_guide.md` is the older self-hosted (Proxmox VM + NetBird) setup, kept for reference.
