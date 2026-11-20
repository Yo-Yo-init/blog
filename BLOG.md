# BLOG.md — how this site works (read before writing a post)

This is the reference the Hermes blog agent follows. Keep it accurate when the site changes.

## Stack
- **Live site:** https://chililab.dev (the old pepperslab.habanada.com redirects here; previews: one URL per branch, shown in the Cloudflare build)
- **Generator:** custom Python static build (`build.py`) using Jinja templates (`templates/`) and Markdown (`content/`).
- **Hosting:** Cloudflare (Workers static assets). Cloudflare runs `pip install -r requirements.txt && python build.py` and serves `dist/`.
- **Branches:** `main` = live site. Any other branch gets its own Cloudflare preview URL. Never push to `main`; open a pull request instead.

## Where things go

| What | Where | Notes |
| --- | --- | --- |
| Blog posts | `content/blog/YYYY-MM-DD-slug.md` | The date prefix is stripped from the URL: `/blog/slug` |
| Docs pages | `content/docs/slug.md` | Ordered by the `order` field |
| Post thumbnails | `static/images/thumbnails/slug.svg` (or `.png`) | Referenced as `/static/images/thumbnails/slug.svg` |
| Other images | `static/images/` | Referenced as `/static/images/...` |

## Post front matter

```yaml
---
title: "Configuring Split DNS on Netbird"
date: 2025-02-19
updated: 2025-03-02      # optional; drives sitemap <lastmod> and JSON-LD dateModified (default: date)
summary: "One or two sentences shown on cards and in search results."
tags: [networking, netbird, dns, vpn]
image: /static/images/thumbnails/configuring-split-dns-on-netbird.svg
hero_alt: "Line drawing of a laptop whose DNS query forks to a house and a globe."  # required with image
draft: false             # true = excluded from the build
---
```

- `hero_alt` is the alt text for the hero image: one descriptive sentence of what the picture shows (not the title, never "Hero Image"). It is also used as `og:image:alt`. The build falls back to the title, but `scripts/check_content.py` fails without a real one.
- `summary` becomes the meta description, og:description and the RSS item text, so write it as a standalone one or two sentences (aim for 160 characters or fewer).
- `author` is optional (default: the site author) and feeds the JSON-LD author.
- `tags` are slugs from `content/tags.yaml` (see **Tags and categories** below). There is no `category:` field any more: the category is derived from the tags.
- Start the body with a short intro paragraph, then `##` / `###` headings (they build the table of contents).
- Code blocks need a language (` ```bash `, ` ```yaml `) for syntax highlighting.

## Thumbnails

Each post has a 16:9 SVG hero at `static/images/thumbnails/<slug>.svg` (800x450). They only show as the hero at the top of a post, so draw them to be read at about 740px wide.

- **Depict the post, not a generic diagram.** Pick the one distinctive object or scene a reader would recognise (a Raspberry Pi board for Pi-hole, a jellyfish for Jellyfin, a gate with a keyhole for Authelia) and make it fill roughly 60 to 80 percent of the frame. Two thumbnails should never be interchangeable.
- **Style:** warm paper plate (`#FAF6EF`) with the dot grid pattern, round-cap line art, stroke width 6 to 10, no text. Palette: chili red `#B5502E`, sage `#6E7F5C`, warm ink `#3B322B`, tints `#F3DACB` (red) and `#DFE6D5` (sage), tan `#CDBFAE`. The solid plate keeps it readable in dark mode.
- **No logos or trademarks.** Evoke the thing (a jellyfish, a board, a winged messenger for Hermes) instead of copying a brand mark.
- **Check before committing:** render the SVG with a spec-accurate renderer and look at it in light and dark. Some quick rasterisers (for example MuPDF) ignore `<pattern>` and dashed strokes and show a black background, which is a tool quirk, not a bug in the file.

## Accessibility rules

- **Headings:** the page template renders the title as the only H1, so a post body starts at `##` and never skips a level (`##` then `####` is an error). Do not repeat the title as `# Title` in the body. Do not wrap headings in bold (`## **Setup**`), headings are already bold.
- **Colours:** muted text, tag chips and accent links must stay at 4.5:1 or better in both themes. Change colours only through the tokens at the top of `static/css/style.css`, and run `python scripts/check_contrast.py`.
- **Structure:** the base template has a "Skip to content" link, labelled nav landmarks, `aria-current` on the active nav item and `aria-pressed` on the theme toggle. Heading anchors (`#`) are `aria-hidden` and not focusable; the table of contents is the keyboard route to a section.
- `python scripts/check_content.py` and `python scripts/check_contrast.py` run in the GitHub check on every pull request.

## Tags and categories

`content/tags.yaml` is the single registry: `tags` maps each slug to its display name (`pihole: Pi-hole`, `llm: LLM`, `netbird: NetBird`), and `categories` are explicit groups of tags. Slugs go in front matter and URLs; the display name is what readers see on chips, pills, tag pages, the feed and JSON-LD.

- **Using a new tag:** add `slug: Display Name` under `tags` first. The build and the GitHub check (`python scripts/check_taxonomy.py`) both fail if a post uses a tag that is not in the registry, and the error suggests the nearest match for typos (`pi-hole` -> `pihole`).
- **Categories are derived, never written by hand.** A post's category is the group that matches the most of its tags; ties go to the higher `priority`. Every post must match at least one group, so give it at least one tag from a group (`homelab`, `proxmox`, `networking`, `hermes-agent` and so on). `troubleshooting` is intentionally in no group.
- **URLs:** each tag has `/blog/tag/<slug>/` and each category `/blog/category/<slug>/`. Tag pages with fewer than 2 posts exist but are `noindex` and out of the sitemap. The old `/blog/?q=<tag>` and `/blog/?category=<slug>` links 301 to these pages (`src/worker.js`).
- **Spelling:** write "homelab" as one word in titles and body text, and use the product spellings from the registry (NetBird, Pi-hole, NGINX, DeepInfra).

## SEO output (generated by `build.py`, do not hand-write)

Every page gets a canonical link, Open Graph and Twitter tags; posts also get `og:type=article`, article times and BlogPosting JSON-LD. The build also writes `sitemap.xml` (published posts and docs only; `<lastmod>` is `updated`, else `date`; pages with no date get none), `robots.txt`, `feed.xml` (RSS 2.0) and `_redirects`.

- **One URL form: trailing slash.** Link to `/blog/<slug>/`, never `/blog/<slug>`. The bare form still works because `dist/_redirects` 301s it, but it costs a hop and a link-check failure. Use `/blog/?q=<tag>` for tag links.
- **Social image:** social networks ignore SVG, so each SVG thumbnail needs a PNG twin at `static/images/og/<slug>.png` (1200x675). After adding or changing a thumbnail run `scripts/make_og_images.py` (instructions in the file) and commit the PNGs. The build prints a WARNING and falls back to the square site card if one is missing.
- Drafts (`draft: true`) are excluded from everything.

## Docs front matter

```yaml
---
title: "Getting Started"
order: 1
---
```

## Build and check locally

```bash
pip install -r requirements.txt
python build.py            # writes dist/
python build.py --serve    # preview at http://localhost:8000
```

The build must finish without errors before pushing.

## Publishing rules (for agents)

1. Draft on a new branch named `draft/<slug>`; commit only the new post and its images.
2. Push the branch; Cloudflare builds a preview. Report the branch name and preview link.
3. Never push to `main`, never force-push, never delete branches you didn't create.
4. Before committing, check the post for secrets and private details: API keys, tokens, passwords, real internal hostnames, public IPs, and anything from the private KB that wasn't meant to be shared. Replace with placeholders (`your_api_key`, `yourdomain.com`, `192.168.1.x`).
5. Never copy private KB files into this repo as-is; write a new post from them.
