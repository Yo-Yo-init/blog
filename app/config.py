# Site-wide configuration

SITE_NAME = "Chili Lab"
SITE_DESCRIPTION = ("Homelab, networking and self-hosted AI agent guides: Proxmox, Pi-hole, Authelia, "
                    "Nginx Proxy Manager and Hermes Agent, with real configs and fixes.")
SITE_AUTHOR = "Pepper"

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
