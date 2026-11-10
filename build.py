"""
Static site build for Cloudflare.

Renders the same Jinja templates and Markdown content that the FastAPI app
(app/main.py) serves, but writes every page to plain HTML files in dist/.
Cloudflare then hosts dist/ as static files -- no Python server needed.

    python build.py            # build into dist/
    python build.py --serve    # build, then preview at http://localhost:8000

Blog search and tag/category filters (/blog?q=..., /blog?category=...) are
handled in the browser by static/js/filter.js, so existing links keep working.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import shutil
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app.config import (  # noqa: E402
    CATEGORIES,
    SITE_AUTHOR,
    SITE_DESCRIPTION,
    SITE_NAME,
    STATIC_DIR,
    TEMPLATES_DIR,
)
from app.content import get_docs, get_posts, refresh_content  # noqa: E402

DIST = ROOT / "dist"

# Optional: set to the live address (e.g. "https://blog.example.com") to get a
# sitemap.xml with absolute URLs. Leave empty to skip the sitemap.
SITE_URL = ""

# Same display helpers as app/main.py, duplicated here so the build does not
# need FastAPI installed.
_ACRONYMS = {"dns", "vpn", "zfs", "nas", "lxc", "ssh", "vm", "nginx"}
_SPECIAL_CASE = {"pihole": "Pi-hole"}


def _display_tag(tag: str) -> str:
    if tag.lower() in _SPECIAL_CASE:
        return _SPECIAL_CASE[tag.lower()]
    words = tag.replace("-", " ").split()
    return " ".join(w.upper() if w.lower() in _ACRONYMS else w.capitalize() for w in words)


def _categories_with_counts() -> list[dict]:
    counts: dict[str, int] = {}
    for post in get_posts():
        counts[post.category] = counts.get(post.category, 0) + 1
    return [{**cat, "count": counts.get(cat["slug"], 0)} for cat in CATEGORIES]


def _top_topics(limit: int | None = 6) -> list[dict]:
    counts: dict[str, int] = {}
    for post in get_posts():
        for tag in post.tags:
            counts[tag] = counts.get(tag, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if limit is not None:
        ranked = ranked[:limit]
    return [{"name": t, "display": _display_tag(t), "count": n} for t, n in ranked]


def _ctx(**kwargs) -> dict:
    return {
        "request": None,
        "site_name": SITE_NAME,
        "site_description": SITE_DESCRIPTION,
        "site_author": SITE_AUTHOR,
        "categories_all": CATEGORIES,
        **kwargs,
    }


def _write(env: Environment, url_path: str, template: str, **ctx) -> str:
    """Render a template to dist/<url_path>/index.html (or dist/404.html)."""
    html = env.get_template(template).render(_ctx(**ctx))
    if url_path.endswith(".html"):
        out = DIST / url_path.lstrip("/")
    else:
        out = DIST / url_path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return url_path


def build() -> None:
    refresh_content()
    posts, docs = get_posts(), get_docs()

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    env = Environment(
        loader=FileSystemLoader(str(ROOT / TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )

    pages = [
        _write(env, "/", "index.html", page_title="Home", posts=posts[:5], recent=posts[:4],
               categories=_categories_with_counts(), topics=_top_topics(), main_class="index-wide"),
        _write(env, "/about/", "about.html", page_title="About"),
        _write(env, "/blog/", "blog_list.html", page_title="Blog", posts=posts, search_query="",
               topics=_top_topics(limit=None), active_category=None),
    ]
    for post in posts:
        pages.append(_write(env, f"/blog/{post.slug}/", "blog_post.html", page_title=post.title,
                            post=post, main_class="post-wide"))
    pages.append(_write(env, "/docs/", "doc_page.html", page_title="Documentation", docs=docs,
                        current=docs[0] if docs else None, main_class="docs-wide"))
    for doc in docs:
        pages.append(_write(env, f"/docs/{doc.slug}/", "doc_page.html", page_title=doc.title,
                            docs=docs, current=doc, main_class="docs-wide"))
    _write(env, "404.html", "404.html", page_title="Page not found")

    shutil.copytree(ROOT / STATIC_DIR, DIST / "static",
                    ignore=shutil.ignore_patterns(".DS_Store"))

    if SITE_URL:
        today = date.today().isoformat()
        urls = "\n".join(
            f"  <url><loc>{escape(SITE_URL.rstrip('/') + p)}</loc><lastmod>{today}</lastmod></url>"
            for p in pages
        )
        (DIST / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n",
            encoding="utf-8",
        )

    print(f"Built {len(pages)} pages ({len(posts)} posts, {len(docs)} docs) into {DIST}")


def serve(port: int = 8000) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Preview at http://localhost:{port}  (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--serve", action="store_true", help="preview dist/ locally after building")
    args = parser.parse_args()
    build()
    if args.serve:
        serve()
