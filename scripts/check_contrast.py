#!/usr/bin/env python3
"""CI check: WCAG 2.x AA contrast for the colour pairs the site actually uses.

Reads the design tokens from static/css/style.css (the `:root` light block and the
`[data-theme="dark"]` block) and computes the contrast ratio with the WCAG relative
luminance formula for every foreground/background pair in PAIRS. Normal text needs 4.5:1,
large text and UI component boundaries 3:1. Exits 1 if any pair fails.

    python scripts/check_contrast.py          # table of every pair
"""
import re
import sys
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "static" / "css" / "style.css"

# (label, foreground token, background token, minimum ratio)
PAIRS = [
    ("body text on page",            "--text",       "--bg",           4.5),
    ("body text on secondary panel", "--text",       "--bg-secondary", 4.5),
    ("muted text (dates, summaries, nav) on page", "--text-muted", "--bg",           4.5),
    ("tag chip text on chip background",           "--text-muted", "--bg-secondary", 4.5),
    ("accent links on page",         "--accent",     "--bg",           4.5),
    ("accent links on secondary",    "--accent",     "--bg-secondary", 4.5),
    ("accent hover on page",         "--accent-hover", "--bg",         4.5),
    ("focus ring (accent outline) vs page, non-text 3:1", "--accent", "--bg", 3.0),
]


def _block(css: str, selector_re: str) -> dict[str, str]:
    m = re.search(selector_re + r"\s*\{(.*?)\n\}", css, re.S)
    if not m:
        sys.exit(f"cannot find CSS block {selector_re!r} in {CSS}")
    return dict(re.findall(r"(--[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\s*;", m.group(1)))


def _lum(hex_color: str) -> float:
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(fg: str, bg: str) -> float:
    a, b = sorted((_lum(fg), _lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def main() -> int:
    css = CSS.read_text(encoding="utf-8")
    light = _block(css, r":root,\s*\[data-theme=\"light\"\]")
    dark = {**light, **_block(css, r"\[data-theme=\"dark\"\]")}
    failures = 0
    for theme, tokens in (("light", light), ("dark", dark)):
        print(f"\n{theme} theme")
        for label, fg, bg, need in PAIRS:
            r = ratio(tokens[fg], tokens[bg])
            ok = r >= need
            failures += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} {r:5.2f}:1 (need {need})  {label}  [{tokens[fg]} on {tokens[bg]}]")
    print(f"\n{'FAIL' if failures else 'OK'}: {failures} pair(s) below the WCAG AA minimum")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
