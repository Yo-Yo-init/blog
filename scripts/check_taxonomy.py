#!/usr/bin/env python3
"""CI check: every tag used by a post must be listed in content/tags.yaml.

Checks all posts in content/blog/ (drafts included, so a draft cannot fail only after it is
published), plus the registry itself: valid slugs, unique display names, category groups that
reference real tags, and every post mapping to a category. Exits 1 with a readable list of
problems. Registry tags that no post uses are reported as a note, not a failure.

    python scripts/check_taxonomy.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import frontmatter  # noqa: E402

from app.taxonomy import TaxonomyError, load_taxonomy  # noqa: E402


def main() -> int:
    try:
        tax = load_taxonomy()
    except TaxonomyError as e:
        print(f"FAIL: {e}")
        return 1

    problems, used, notes = [], set(), []
    posts = sorted((ROOT / "content" / "blog").glob("*.md"))
    for md in posts:
        meta = frontmatter.load(str(md)).metadata
        tags = meta.get("tags") or []
        if not isinstance(tags, list):
            problems.append(f"{md.name}: `tags` must be a list, e.g. tags: [homelab, proxmox]")
            continue
        tags = [str(t) for t in tags]
        used.update(tags)
        problems += tax.check_post(md.name, tags)
        if "category" in meta:
            notes.append(f"{md.name}: `category:` is ignored now (derived from tags); remove it")

    for n in notes:
        print("NOTE:", n)
    unused = sorted(set(tax.tags) - used)
    if unused:
        print("NOTE: registry tags no post uses:", ", ".join(unused))
    if problems:
        print("\nFAIL: taxonomy problems")
        for p in problems:
            print("  -", p)
        print("\nFix: add the tag to content/tags.yaml (slug: Display Name) or correct the post.")
        return 1
    print(f"OK: {len(posts)} posts, {len(used)} tags in use, all present in content/tags.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
