# Site-wide configuration

SITE_NAME = "Chili Lab"
SITE_DESCRIPTION = ("Homelab, networking and self-hosted AI agent guides: Proxmox, Pi-hole, Authelia, "
                    "Nginx Proxy Manager and Hermes Agent, with real configs and fixes.")
SITE_AUTHOR = "Pepper"

# Footer copyright range: first year the site published, to the year of the build.
from datetime import date as _date  # noqa: E402

SITE_START_YEAR = 2025
_this_year = _date.today().year
COPYRIGHT_YEARS = (f"{SITE_START_YEAR}\u2013{_this_year}" if _this_year > SITE_START_YEAR
                   else str(SITE_START_YEAR))

# Social links shown in the footer and on /about/.
# TODO: YOUTUBE_URL still points at a single video (the old footer link). Replace it with the
# channel URL (https://www.youtube.com/@<handle>) once it is known; nothing else needs to change.
YOUTUBE_URL = "https://www.youtube.com/watch?v=3BFTio5296w"

# Paths (relative to project root)
CONTENT_DIR = "content"
BLOG_DIR = "content/blog"
DOCS_DIR = "content/docs"
STATIC_DIR = "static"
TEMPLATES_DIR = "templates"

# Categories come from the tag registry (content/tags.yaml): one definition, no drift.
# Each entry: slug, name, icon, desc. Posts get a category from their tags, never from
# front matter. ('icon' refers to an id handled in templates/_icons.html.)
from app.taxonomy import get_taxonomy  # noqa: E402

CATEGORIES = [
    {"slug": c.slug, "name": c.name, "icon": c.icon, "desc": c.desc}
    for c in get_taxonomy().categories
]
