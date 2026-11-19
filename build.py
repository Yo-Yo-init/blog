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
import re
import shutil
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
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

# Live address. Drives canonical links, og:url, the sitemap, the feed and the
# JSON-LD. Leave empty to build without any SEO output (local-only builds).
SITE_URL = "https://chililab.dev"

# Canonical URL form: every page lives at /path/ (trailing slash), matching the
# dist/<path>/index.html layout. build() writes dist/_redirects so the bare
# /path form answers with a 301 to it.

# Social cards. Facebook, LinkedIn and X ignore SVG og:images, so each SVG hero
# has a PNG twin in static/images/og/ (made by scripts/make_og_images.py).
OG_DIR = ROOT / "static" / "images" / "og"
OG_SITE_IMAGE = ("/static/images/og/site.png", 640, 640)   # square, for pages without a hero
OG_POST_SIZE = (1200, 675)

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


def _abs(path: str) -> str:
    """Absolute URL for a site path."""
    return SITE_URL.rstrip("/") + path


def _plain_first_paragraph(html: str, limit: int = 155) -> str:
    """Fallback meta description: first <p> of rendered HTML, tags stripped."""
    m = re.search(r"<p>(.*?)</p>", html, re.S)
    text = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "..."


def _post_og_image(post) -> tuple[str, int, int]:
    """(site path, width, height) of the social image for a post."""
    img = post.image or ""
    stem = Path(img).stem
    if img and (OG_DIR / f"{stem}.png").exists():
        return (f"/static/images/og/{stem}.png", *OG_POST_SIZE)
    if img.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        return (img, 0, 0)  # raster hero already: use as-is, size unknown
    print(f"WARNING: no social PNG for post '{post.slug}' (run scripts/make_og_images.py); "
          f"using the site card", file=sys.stderr)
    return OG_SITE_IMAGE


def _seo(path: str, *, title: str, description: str, og_type: str = "website",
         image: tuple[str, int, int] | None = None, image_alt: str = "",
         canonical_path: str | None = None, jsonld: dict | None = None,
         article: dict | None = None, noindex: bool = False) -> dict | None:
    """Per-page SEO data consumed by templates/base.html. None when SITE_URL is unset."""
    if not SITE_URL:
        return None
    img_path, img_w, img_h = image or OG_SITE_IMAGE
    canon = _abs(canonical_path or path)
    return {
        "site_url": SITE_URL.rstrip("/"),
        "title": title,
        "description": description,
        "type": og_type,
        "canonical": None if noindex else canon,
        "url": canon,
        "noindex": noindex,
        "image": _abs(img_path),
        "image_w": img_w, "image_h": img_h,
        "image_alt": image_alt or title,
        "twitter_card": "summary_large_image" if img_w and img_w > img_h else "summary",
        "jsonld": jsonld,
        "article": article,
    }


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

    newest = max((p.modified for p in posts), default=None)
    pages: list[str] = []          # every indexable URL path (feeds the sitemap)
    lastmod: dict[str, datetime | None] = {}

    def add(path: str, template: str, mod: datetime | None = None, *, in_sitemap: bool = True,
            **ctx) -> None:
        _write(env, path, template, **ctx)
        pages.append(path)
        if in_sitemap:
            lastmod[path] = mod

    add("/", "index.html", newest, page_title="Home", posts=posts[:5], recent=posts[:4],
        categories=_categories_with_counts(), topics=_top_topics(), main_class="with-sidebar",
        seo=_seo("/", title=SITE_NAME, description=SITE_DESCRIPTION))
    add("/about/", "about.html", None, page_title="About",
        seo=_seo("/about/", title=f"About — {SITE_NAME}", description=SITE_DESCRIPTION))
    add("/blog/", "blog_list.html", newest, page_title="Blog", posts=posts, search_query="",
        topics=_top_topics(limit=None), active_category=None,
        categories=_categories_with_counts(), main_class="with-sidebar",
        seo=_seo("/blog/", title=f"Blog — {SITE_NAME}", description=SITE_DESCRIPTION))

    for post in posts:
        path = f"/blog/{post.slug}/"
        desc = post.summary.strip() or _plain_first_paragraph(post.content_html) or SITE_DESCRIPTION
        author = post.author or SITE_AUTHOR
        image = _post_og_image(post)
        published = post.date.date().isoformat()
        modified = post.modified.date().isoformat()
        cat = next((c["name"] for c in CATEGORIES if c["slug"] == post.category), None)
        jsonld = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "mainEntityOfPage": {"@type": "WebPage", "@id": _abs(path)},
            "headline": post.title,
            "description": desc,
            "image": [_abs(image[0])],
            "datePublished": published,
            "dateModified": modified,
            "author": {"@type": "Person", "name": author, "url": _abs("/about/")},
            "url": _abs(path),
            "inLanguage": "en",
        }
        if post.tags:
            jsonld["keywords"] = ", ".join(post.tags)
        if cat:
            jsonld["articleSection"] = cat
        article = {"published": published, "modified": modified, "author": author,
                   "section": cat, "tags": list(post.tags)}
        add(path, "blog_post.html", post.modified, page_title=post.title, post=post,
            main_class="post-wide",
            seo=_seo(path, title=post.title, description=desc, og_type="article", image=image,
                     image_alt=post.title, jsonld=jsonld, article=article))

    # /docs/ renders the first doc, so it is a duplicate: canonical points at that doc
    # and it stays out of the sitemap.
    docs_canonical = f"/docs/{docs[0].slug}/" if docs else "/docs/"
    add("/docs/", "doc_page.html", None, in_sitemap=False, page_title="Documentation", docs=docs,
        current=docs[0] if docs else None, main_class="docs-wide",
        seo=_seo("/docs/", title=f"Documentation — {SITE_NAME}", description=SITE_DESCRIPTION,
                 canonical_path=docs_canonical))
    for doc in docs:
        path = f"/docs/{doc.slug}/"
        add(path, "doc_page.html", doc.modified, page_title=doc.title, docs=docs, current=doc,
            main_class="docs-wide",
            seo=_seo(path, title=f"{doc.title} — {SITE_NAME}", description=SITE_DESCRIPTION))
    _write(env, "404.html", "404.html", page_title="Page not found",
           seo=_seo("/404/", title=f"Page not found — {SITE_NAME}", description=SITE_DESCRIPTION,
                    noindex=True))

    shutil.copytree(ROOT / STATIC_DIR, DIST / "static",
                    ignore=shutil.ignore_patterns(".DS_Store"))

    if SITE_URL:
        _write_sitemap(lastmod)
        _write_robots()
        _write_feed(posts)
    _write_redirects(pages)

    print(f"Built {len(pages)} pages ({len(posts)} posts, {len(docs)} docs) into {DIST}")


def _write_sitemap(lastmod: dict[str, datetime | None]) -> None:
    """sitemap.xml: published posts and docs only (drafts never load). <lastmod> comes from
    frontmatter (`updated`, else `date`); pages without a date get no <lastmod> rather than
    a made-up one."""
    rows = []
    for path, mod in lastmod.items():
        lm = f"<lastmod>{mod.date().isoformat()}</lastmod>" if mod else ""
        rows.append(f"  <url><loc>{escape(_abs(path))}</loc>{lm}</url>")
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")


def _write_robots() -> None:
    """robots.txt. Cloudflare's managed robots.txt (content-signal comments) is merged in
    front of this file at the edge."""
    (DIST / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {_abs('/sitemap.xml')}\n", encoding="utf-8")


def _write_feed(posts) -> None:
    """RSS 2.0 at /feed.xml: title, link, summary, date and tags for every published post."""
    def rfc822(d: datetime) -> str:
        return format_datetime(d.replace(hour=12, tzinfo=timezone.utc))  # date-only source: noon UTC

    items = []
    for p in posts:
        link = escape(_abs(f"/blog/{p.slug}/"))
        desc = p.summary.strip() or _plain_first_paragraph(p.content_html)
        cats = "".join(f"<category>{escape(t)}</category>" for t in p.tags)
        items.append(
            f"    <item>\n      <title>{escape(p.title)}</title>\n      <link>{link}</link>\n"
            f'      <guid isPermaLink="true">{link}</guid>\n'
            f"      <pubDate>{rfc822(p.date)}</pubDate>\n"
            f"      <description>{escape(desc)}</description>\n"
            f"      {cats}\n    </item>")
    built = rfc822(max((p.modified for p in posts), default=datetime(2000, 1, 1)))
    (DIST / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n  <channel>\n'
        f"    <title>{escape(SITE_NAME)}</title>\n"
        f"    <link>{escape(_abs('/'))}</link>\n"
        f"    <description>{escape(SITE_DESCRIPTION)}</description>\n"
        "    <language>en</language>\n"
        f"    <lastBuildDate>{built}</lastBuildDate>\n"
        f'    <atom:link href="{escape(_abs("/feed.xml"))}" rel="self" type="application/rss+xml" />\n'
        + "\n".join(items) + "\n  </channel>\n</rss>\n", encoding="utf-8")


def _write_redirects(pages: list[str]) -> None:
    """dist/_redirects (Cloudflare static assets): 301 the bare /path form to /path/."""
    rules = [f"{p.rstrip('/')} {p} 301" for p in pages if p != "/" and p.endswith("/")]
    (DIST / "_redirects").write_text("\n".join(rules) + "\n", encoding="utf-8")


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
