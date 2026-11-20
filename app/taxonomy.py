"""
Tag and category registry (content/tags.yaml).

One place defines every tag slug and its display name, and which tags make up
each category. Categories are derived from a post's tags, so counts and pages
cannot drift. Imported by app.content (to validate and decorate posts), by
build.py (tag and category pages) and by scripts/check_taxonomy.py (CI).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "content" / "tags.yaml"
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class TaxonomyError(Exception):
    """Raised with a readable, multi-line message when the registry or a post is invalid."""


@dataclass
class Category:
    slug: str
    name: str
    desc: str
    icon: str
    priority: int
    tags: list[str] = field(default_factory=list)


class Taxonomy:
    def __init__(self, tags: dict[str, str], categories: list[Category]):
        self.tags = tags
        self.categories = categories
        self._tag_to_cat = {t: c.slug for c in categories for t in c.tags}

    # ---- lookups -------------------------------------------------------
    def tag_name(self, slug: str) -> str:
        return self.tags[slug]

    def category(self, slug: str) -> Category | None:
        return next((c for c in self.categories if c.slug == slug), None)

    def primary_category(self, tag_slugs: list[str]) -> Category | None:
        """Most matching tags wins; ties go to the higher `priority`; None if nothing matches."""
        best, best_key = None, (0, 0)
        for cat in self.categories:
            score = sum(1 for t in tag_slugs if t in cat.tags)
            if score and (score, cat.priority) > best_key:
                best, best_key = cat, (score, cat.priority)
        return best

    # ---- validation ----------------------------------------------------
    def check_post(self, label: str, tag_slugs: list[str]) -> list[str]:
        """Problems with one post's tags, as human-readable lines (empty list = fine)."""
        problems = []
        if not tag_slugs:
            problems.append(f"{label}: has no tags")
        for t in tag_slugs:
            if t not in self.tags:
                near = [k for k in self.tags if k.replace("-", "") == str(t).lower().replace("-", "").replace(" ", "")]
                hint = f" (did you mean '{near[0]}'?)" if near else ""
                problems.append(f"{label}: tag '{t}' is not in content/tags.yaml{hint}")
        if len(set(tag_slugs)) != len(tag_slugs):
            problems.append(f"{label}: duplicate tags {sorted({t for t in tag_slugs if tag_slugs.count(t) > 1})}")
        known = [t for t in tag_slugs if t in self.tags]
        if known and self.primary_category(known) is None:
            problems.append(f"{label}: none of its tags belongs to a category group in content/tags.yaml")
        return problems


def load_taxonomy(path: Path | None = None) -> Taxonomy:
    path = Path(path or REGISTRY_PATH)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as e:
        raise TaxonomyError(f"cannot read {path}: {e}") from e

    errors: list[str] = []
    tags = raw.get("tags") or {}
    if not isinstance(tags, dict) or not tags:
        raise TaxonomyError(f"{path}: `tags` must be a non-empty mapping of slug -> display name")
    for slug, name in tags.items():
        if not isinstance(slug, str) or not _SLUG_RE.match(slug):
            errors.append(f"tag slug '{slug}' must be lowercase letters, digits and hyphens")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"tag '{slug}' needs a display name")
    names = [n for n in tags.values() if isinstance(n, str)]
    for n in {n for n in names if names.count(n) > 1}:
        errors.append(f"display name '{n}' is used by more than one tag")

    categories: list[Category] = []
    seen_cat, seen_tag = set(), {}
    for c in raw.get("categories") or []:
        slug = c.get("slug", "")
        if slug in seen_cat or not _SLUG_RE.match(str(slug)):
            errors.append(f"category slug '{slug}' is invalid or duplicated")
        seen_cat.add(slug)
        for t in c.get("tags") or []:
            if t not in tags:
                errors.append(f"category '{slug}' lists unknown tag '{t}'")
            if t in seen_tag:
                errors.append(f"tag '{t}' is in two category groups ('{seen_tag[t]}' and '{slug}')")
            seen_tag[t] = slug
        categories.append(Category(slug=slug, name=c.get("name", slug), desc=c.get("desc", ""),
                                   icon=c.get("icon", "server"), priority=int(c.get("priority", 0)),
                                   tags=list(c.get("tags") or [])))
    if not categories:
        errors.append("`categories` must define at least one category")
    if errors:
        raise TaxonomyError(f"{path} is invalid:\n  - " + "\n  - ".join(errors))
    return Taxonomy(dict(tags), categories)


_cached: Taxonomy | None = None


def get_taxonomy() -> Taxonomy:
    global _cached
    if _cached is None:
        _cached = load_taxonomy()
    return _cached
