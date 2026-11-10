"""
FastAPI application — routes, static files, template rendering.
"""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from watchfiles import awatch

from app.config import (
    SITE_NAME,
    SITE_DESCRIPTION,
    SITE_AUTHOR,
    CONTENT_DIR,
    STATIC_DIR,
    TEMPLATES_DIR,
    CATEGORIES,
)
from app.content import refresh_content, get_posts, get_docs

logger = logging.getLogger("uvicorn.error")


# ---------------------------------------------------------------------------
# Background content watcher
# ---------------------------------------------------------------------------

async def _watch_content():
    """Watch the content directory for .md file changes and refresh the cache."""
    try:
        async for changes in awatch(CONTENT_DIR):
            md_changes = [path for _, path in changes if path.endswith(".md")]
            if md_changes:
                logger.info("📝 Content change detected — refreshing cache...")
                refresh_content()
                logger.info("✅ Cache refreshed (%d posts loaded)", len(get_posts()))
    except asyncio.CancelledError:
        pass


# ---------------------------------------------------------------------------
# Lifespan — load content on startup, start file watcher
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    refresh_content()
    logger.info("🚀 Loaded %d posts on startup", len(get_posts()))
    watcher_task = asyncio.create_task(_watch_content())
    yield
    watcher_task.cancel()
    await watcher_task


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title=SITE_NAME, lifespan=lifespan, docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ---------------------------------------------------------------------------
# Template context helper
# ---------------------------------------------------------------------------

def _ctx(request: Request, **kwargs) -> dict:
    """Build the base template context."""
    return {
        "request": request,
        "site_name": SITE_NAME,
        "site_description": SITE_DESCRIPTION,
        "site_author": SITE_AUTHOR,
        "categories_all": CATEGORIES,
        **kwargs,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

# Tags that should render as acronyms rather than title-cased words.
_ACRONYMS = {"dns", "vpn", "zfs", "nas", "lxc", "ssh", "vm", "nginx"}
# Tags with a specific preferred display form.
_SPECIAL_CASE = {"pihole": "Pi-hole"}


def _display_tag(tag: str) -> str:
    if tag.lower() in _SPECIAL_CASE:
        return _SPECIAL_CASE[tag.lower()]
    words = tag.replace("-", " ").split()
    return " ".join(w.upper() if w.lower() in _ACRONYMS else w.capitalize() for w in words)


def _categories_with_counts() -> list[dict]:
    """Merge the static category definitions with real post counts."""
    counts = Counter(post.category for post in get_posts())
    return [{**cat, "count": counts.get(cat["slug"], 0)} for cat in CATEGORIES]


def _top_topics(limit: int | None = 6) -> list[dict]:
    """Build a topic list from real tag frequency across all posts."""
    counts = Counter(tag for post in get_posts() for tag in post.tags)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if limit is not None:
        ranked = ranked[:limit]
    return [{"name": tag, "display": _display_tag(tag), "count": n} for tag, n in ranked]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", _ctx(
        request,
        page_title="Home",
        posts=get_posts()[:5],
        recent=get_posts()[:4],
        categories=_categories_with_counts(),
        topics=_top_topics(),
        main_class="index-wide",
    ))


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", _ctx(
        request,
        page_title="About",
    ))


@app.get("/blog", response_class=HTMLResponse)
async def blog_list(request: Request, q: str = "", category: str = ""):
    posts = get_posts()
    if category:
        posts = [p for p in posts if p.category == category]
    if q:
        q_lower = q.lower()
        posts = [
            p for p in posts
            if q_lower in p.title.lower()
            or q_lower in p.summary.lower()
            or any(q_lower in t.lower() for t in p.tags)
        ]
    active_category = next((c for c in CATEGORIES if c["slug"] == category), None)
    return templates.TemplateResponse("blog_list.html", _ctx(
        request,
        page_title="Blog",
        posts=posts,
        search_query=q,
        topics=_top_topics(limit=None),
        active_category=active_category,
    ))


@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str):
    posts = get_posts()
    post = next((p for p in posts if p.slug == slug), None)
    if post is None:
        return HTMLResponse("<h1>404 — Post not found</h1>", status_code=404)
    return templates.TemplateResponse("blog_post.html", _ctx(
        request,
        page_title=post.title,
        post=post,
        main_class="post-wide",
    ))


@app.get("/docs", response_class=HTMLResponse)
async def docs_index(request: Request):
    docs = get_docs()
    current = docs[0] if docs else None
    return templates.TemplateResponse("doc_page.html", _ctx(
        request,
        page_title="Documentation",
        docs=docs,
        current=current,
        main_class="docs-wide",
    ))


@app.get("/docs/{slug}", response_class=HTMLResponse)
async def docs_page(request: Request, slug: str):
    docs = get_docs()
    current = next((d for d in docs if d.slug == slug), None)
    if current is None:
        return HTMLResponse("<h1>404 — Doc not found</h1>", status_code=404)
    return templates.TemplateResponse("doc_page.html", _ctx(
        request,
        page_title=current.title,
        docs=docs,
        current=current,
        main_class="docs-wide",
    ))
