# Site-wide configuration

SITE_NAME = "Pepper's Lab"
SITE_DESCRIPTION = "Cybersecurity notes, homelab builds, and documentation."
SITE_AUTHOR = "Pepper"

# Paths (relative to project root)
CONTENT_DIR = "content"
BLOG_DIR = "content/blog"
DOCS_DIR = "content/docs"
STATIC_DIR = "static"
TEMPLATES_DIR = "templates"

# Top-level content pillars shown as tiles on the homepage. Order here is
# display order — homelab first since it's the deepest category today.
# 'icon' refers to an id handled in templates/_icons.html.
CATEGORIES = [
    {"slug": "homelab", "name": "Homelab", "icon": "server",
     "desc": "Proxmox, networking, and self-hosted services"},
    {"slug": "retro-gaming", "name": "Retro gaming", "icon": "gamepad",
     "desc": "Old hardware, emulation, and restorations"},
    {"slug": "certs", "name": "Certs & study notes", "icon": "certificate",
     "desc": "Study logs and exam notes"},
    {"slug": "musings", "name": "Musings", "icon": "feather",
     "desc": "Everything that doesn't fit elsewhere"},
]
