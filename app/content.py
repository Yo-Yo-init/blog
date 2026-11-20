"""
Content pipeline — loads Markdown files, parses frontmatter, renders HTML.
"""

from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime

import frontmatter
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

from app.config import BLOG_DIR, DOCS_DIR
from app.taxonomy import TaxonomyError, get_taxonomy


# ---------------------------------------------------------------------------
# Syntax-highlighted code renderer for mistune v3
# ---------------------------------------------------------------------------

_formatter = HtmlFormatter(nowrap=True)


class HighlightRenderer(mistune.HTMLRenderer):
    """Extends the built-in HTML renderer with Pygments syntax highlighting."""

    def block_code(self, code, info=None, **attrs):
        lang = info.split()[0] if info else None

        if lang:
            try:
                lexer = get_lexer_by_name(lang, stripall=True)
            except Exception:
                lexer = guess_lexer(code)
        else:
            lexer = guess_lexer(code)

        highlighted = highlight(code, lexer, _formatter)
        lang_class = f' class="language-{lang}"' if lang else ""
        return f"<pre><code{lang_class}>{highlighted}</code></pre>\n"


# ---------------------------------------------------------------------------
# Markdown parser instance
# ---------------------------------------------------------------------------

# GFM plugins: `table` is required for markdown tables to render as <table>
# instead of raw pipes (mistune v3 keeps tables behind a plugin). `strikethrough`
# and `task_lists` match GitHub-flavored formatting. `url` autolinking is left
# off on purpose so existing links/text are not rewritten.
_md = mistune.create_markdown(
    renderer=HighlightRenderer(),
    plugins=["table", "strikethrough", "task_lists"],
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

class Post:
    """Represents a blog post."""

    def __init__(self, slug: str, title: str, date: datetime, summary: str,
                 tags: list[str], image: str, content_html: str, draft: bool = False,
                 updated: datetime | None = None, author: str = "", hero_alt: str = ""):
        self.slug = slug
        self.title = title
        self.date = date
        self.summary = summary
        self.tags = tags
        self.image = image
        self.content_html = content_html
        self.draft = draft
        self.updated = updated      # optional `updated:` frontmatter
        self.hero_alt = hero_alt    # alt text for the hero image (required when `image:` is set)
        self.author = author        # optional `author:` frontmatter

    @property
    def tag_chips(self) -> list[dict]:
        """Tags as {slug, name, url}: display name for the chip, slug for the URL."""
        tax = get_taxonomy()
        return [{"slug": t, "name": tax.tag_name(t), "url": f"/blog/tag/{t}/"} for t in self.tags]

    @property
    def category(self) -> str:
        """Slug of the category derived from this post's tags (see content/tags.yaml)."""
        cat = get_taxonomy().primary_category(self.tags)
        return cat.slug if cat else ""

    @property
    def category_name(self) -> str:
        cat = get_taxonomy().primary_category(self.tags)
        return cat.name if cat else ""

    @property
    def modified(self) -> datetime:
        """Last-modified moment for sitemap/JSON-LD: `updated` if set, else `date`."""
        return self.updated or self.date

    @property
    def date_display(self) -> str:
        return self.date.strftime("%B %d, %Y")


class DocPage:
    """Represents a documentation page."""

    def __init__(self, slug: str, title: str, order: int, content_html: str,
                 modified: datetime | None = None):
        self.slug = slug
        self.title = title
        self.order = order
        self.content_html = content_html
        self.modified = modified    # `updated:` else `date:` frontmatter, else None


# ---------------------------------------------------------------------------
# Content loaders
# ---------------------------------------------------------------------------

# In-memory cache
_posts_cache: list[Post] = []
_docs_cache: list[DocPage] = []


def _slug_from_filename(filename: str) -> str:
    """Derive a URL slug from a markdown filename.

    '2025-01-15-hello-world.md' -> 'hello-world'
    'getting-started.md'        -> 'getting-started'
    """
    name = Path(filename).stem
    # Strip leading date pattern (YYYY-MM-DD-)
    name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
    return name


def _as_datetime(val) -> datetime | None:
    """Coerce a frontmatter date (datetime, date or ISO string) to a naive datetime."""
    if val is None or val == "":
        return None
    if isinstance(val, datetime):
        return val.replace(tzinfo=None)
    if isinstance(val, str):
        return datetime.fromisoformat(val).replace(tzinfo=None)
    return datetime(val.year, val.month, val.day)  # datetime.date


def load_posts() -> list[Post]:
    """Load all blog posts from BLOG_DIR, newest first. Filters out drafts."""
    posts: list[Post] = []
    blog_path = Path(BLOG_DIR)

    if not blog_path.exists():
        return posts

    for filepath in sorted(blog_path.glob("*.md")):
        post_data = frontmatter.load(str(filepath))
        meta = post_data.metadata

        if meta.get("draft", False):
            continue

        date_val = meta.get("date", datetime(2000, 1, 1))
        if isinstance(date_val, str):
            date_val = datetime.fromisoformat(date_val)
        elif not isinstance(date_val, datetime):
            # Handle date objects
            date_val = datetime(date_val.year, date_val.month, date_val.day)

        posts.append(Post(
            slug=_slug_from_filename(filepath.name),
            title=meta.get("title", filepath.stem),
            date=date_val,
            summary=meta.get("summary", ""),
            tags=meta.get("tags", []),
            image=meta.get("image", ""),
            content_html=_md(post_data.content),
            draft=False,
            updated=_as_datetime(meta.get("updated")),
            author=str(meta.get("author", "") or ""),
            hero_alt=str(meta.get("hero_alt", "") or "").strip(),
        ))

    # Every tag must be in content/tags.yaml and map to a category: fail the build, loudly.
    tax = get_taxonomy()
    problems = [msg for p in posts for msg in tax.check_post(f"content/blog/*-{p.slug}.md", p.tags)]
    if problems:
        raise TaxonomyError("Tag problems:\n  - " + "\n  - ".join(problems))

    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def load_docs() -> list[DocPage]:
    """Load all doc pages from DOCS_DIR, sorted by 'order' frontmatter field."""
    docs: list[DocPage] = []
    docs_path = Path(DOCS_DIR)

    if not docs_path.exists():
        return docs

    for filepath in sorted(docs_path.glob("*.md")):
        doc_data = frontmatter.load(str(filepath))
        meta = doc_data.metadata

        docs.append(DocPage(
            slug=_slug_from_filename(filepath.name),
            title=meta.get("title", filepath.stem),
            order=meta.get("order", 99),
            content_html=_md(doc_data.content),
            modified=_as_datetime(meta.get("updated")) or _as_datetime(meta.get("date")),
        ))

    docs.sort(key=lambda d: d.order)
    return docs


def refresh_content():
    """Reload all content from disk into the cache."""
    global _posts_cache, _docs_cache
    _posts_cache = load_posts()
    _docs_cache = load_docs()


def get_posts() -> list[Post]:
    return _posts_cache


def get_docs() -> list[DocPage]:
    return _docs_cache
