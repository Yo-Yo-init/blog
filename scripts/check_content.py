#!/usr/bin/env python3
"""CI check: accessibility rules for post content.

For every post in content/blog/ (drafts included):
  * the body has no H1 (the page template already renders the title as the one H1);
  * the first heading in the body is an H2, and levels never skip (H2 -> H4 is an error);
  * headings are not wrapped in bold/strong (**Heading**), headings are already bold;
  * when `image:` is set there is a descriptive `hero_alt:` (not "Hero Image", not just the
    title, at least 5 words), because the hero is a content image, not decoration.

    python scripts/check_content.py
"""
import re
import sys
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parent.parent


def headings(body: str):
    code = False
    for n, line in enumerate(body.splitlines(), 1):
        if line.strip().startswith("```"):
            code = not code
            continue
        if code:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            yield n, len(m.group(1)), m.group(2)


def main() -> int:
    problems = []
    series_members: dict[str, list[str]] = {}   # series name -> published posts in it
    posts = sorted((ROOT / "content" / "blog").glob("*.md"))
    for md in posts:
        post = frontmatter.load(str(md))
        name, prev = md.name, 1          # the page H1 counts as level 1
        for n, lvl, text in headings(post.content):
            if lvl == 1:
                problems.append(f"{name}: body line {n}: H1 '{text[:40]}' (the title is already the page H1; remove it or use ##)")
                continue
            if lvl > prev + 1:
                problems.append(f"{name}: body line {n}: heading jumps from H{prev} to H{lvl} ('{text[:40]}')")
            if re.match(r"^(\*\*|__).+(\*\*|__)$", text):
                problems.append(f"{name}: body line {n}: heading wrapped in bold ('{text[:40]}'), remove the ** **")
            prev = lvl
        if post.metadata.get("image"):
            alt = str(post.metadata.get("hero_alt") or "").strip()
            title = str(post.metadata.get("title") or "").strip()
            if not alt:
                problems.append(f"{name}: has `image:` but no `hero_alt:` (describe what the picture shows)")
            elif alt.lower() in {"hero image", "image", "thumbnail"} or alt.lower() == title.lower() or len(alt.split()) < 5:
                problems.append(f"{name}: hero_alt is not descriptive ('{alt[:50]}')")
        if post.metadata.get("draft"):
            continue
        series = str(post.metadata.get("series") or "").strip()
        if series:
            series_members.setdefault(series, []).append(name)
    for series, members in sorted(series_members.items()):
        if len(members) < 2:
            problems.append(f"{members[0]}: series '{series}' has only one post (a series needs at least two, check the spelling)")
    if problems:
        print("FAIL: content accessibility problems")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: {len(posts)} posts: heading structure, hero_alt and series")
    return 0


if __name__ == "__main__":
    sys.exit(main())
