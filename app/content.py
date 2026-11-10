"""
Content pipeline — loads Markdown files, parses frontmatter, renders HTML.
"""

import re
from pathlib import Path
from datetime import datetime

import frontmatter
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

from app.config import BLOG_DIR, DOCS_DIR


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

_md = mistune.create_markdown(renderer=HighlightRenderer())


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

class Post:
    """Represents a blog post."""

    def __init__(self, slug: str, title: str, date: datetime, summary: str,
                 tags: list[str], image: str, content_html: str, draft: bool = False,
                 category: str = "homelab"):
        self.slug = slug
        self.title = title
        self.date = date
        self.summary = summary
        self.tags = tags
        self.image = image
        self.content_html = content_html
        self.draft = draft
        self.category = category

    @property
    def date_display(self) -> str:
        return self.date.strftime("%B %d, %Y")


class DocPage:
    """Represents a documentation page."""

    def __init__(self, slug: str, title: str, order: int, content_html: str):
        self.slug = slug
        self.title = title
        self.order = order
        self.content_html = content_html


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
            category=meta.get("category", "homelab"),
        ))

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
