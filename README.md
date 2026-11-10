# Pepper's Lab

Cybersecurity notes, homelab builds, and documentation. Markdown content rendered with Jinja templates into a static site, hosted on Cloudflare.

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

Add Markdown files to `content/blog/` (posts) or `content/docs/` (docs). Front matter, folders and publishing rules are in [BLOG.md](BLOG.md).

## Deployment

Cloudflare builds every push:

| Setting | Value |
| --- | --- |
| Build command | `pip install -r requirements.txt && python build.py` |
| Output | `dist/` (set in `wrangler.jsonc`) |
| Production branch | `main` |
| Previews | every other branch |

`hosting_guide.md` is the older self-hosted (Proxmox VM + NetBird) setup, kept for reference.
