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

# Top-level content categories (sidebar + /blog?category=<slug>). Order here is
# display order. Only list categories that have posts; add one here when the
# first post for it exists.
# 'icon' refers to an id handled in templates/_icons.html.
CATEGORIES = [
    {"slug": "homelab", "name": "Homelab", "icon": "server",
     "desc": "Builds, storage, and Proxmox hosts"},
    {"slug": "ai", "name": "AI & agents", "icon": "server",
     "desc": "Hermes agents, model choices, and running them for real"},
    {"slug": "networking", "name": "Networking & security", "icon": "server",
     "desc": "DNS, VPNs, reverse proxies, and locking things down"},
]
