# BLOG.md — how this site works (read before writing a post)

This is the reference the Hermes blog agent follows. Keep it accurate when the site changes.

## Stack

- **Generator:** custom Python static build (`build.py`) using Jinja templates (`templates/`) and Markdown (`content/`).
- **Hosting:** Cloudflare (Workers static assets). Cloudflare runs `pip install -r requirements.txt && python build.py` and serves `dist/`.
- **Branches:** `main` = live site. Any other branch gets its own Cloudflare preview URL. Never push to `main`; open a pull request instead.

## Where things go

| What | Where | Notes |
| --- | --- | --- |
| Blog posts | `content/blog/YYYY-MM-DD-slug.md` | The date prefix is stripped from the URL: `/blog/slug` |
| Docs pages | `content/docs/slug.md` | Ordered by the `order` field |
| Post thumbnails | `static/images/thumbnails/slug.svg` (or `.png`) | Referenced as `/static/images/thumbnails/slug.svg` |
| Other images | `static/images/` | Referenced as `/static/images/...` |

## Post front matter

```yaml
---
title: "Configuring Split DNS on Netbird"
date: 2025-02-19
summary: "One or two sentences shown on cards and in search results."
tags: [networking, netbird, dns, vpn]
image: /static/images/thumbnails/configuring-split-dns-on-netbird.svg
category: homelab        # homelab | retro-gaming | certs | musings
draft: false             # true = excluded from the build
---
```

- Tags are lowercase and hyphenated (`home-assistant`, not `Home Assistant`). Reuse existing tags where they fit.
- `category` must be one of the four slugs in `app/config.py`.
- Start the body with a short intro paragraph, then `##` / `###` headings (they build the table of contents).
- Code blocks need a language (` ```bash `, ` ```yaml `) for syntax highlighting.

## Docs front matter

```yaml
---
title: "Getting Started"
order: 1
---
```

## Build and check locally

```bash
pip install -r requirements.txt
python build.py            # writes dist/
python build.py --serve    # preview at http://localhost:8000
```

The build must finish without errors before pushing.

## Publishing rules (for agents)

1. Draft on a new branch named `draft/<slug>`; commit only the new post and its images.
2. Push the branch; Cloudflare builds a preview. Report the branch name and preview link.
3. Never push to `main`, never force-push, never delete branches you didn't create.
4. Before committing, check the post for secrets and private details: API keys, tokens, passwords, real internal hostnames, public IPs, and anything from the private KB that wasn't meant to be shared. Replace with placeholders (`your_api_key`, `yourdomain.com`, `192.168.1.x`).
5. Never copy private KB files into this repo as-is; write a new post from them.
