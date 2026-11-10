---
title: "Getting Started"
order: 1
---

Welcome to the documentation section. This is where I keep structured reference material — guides, runbooks, and notes that don't fit the chronological blog format.

## How This Site Works

Content is written in **Markdown** files with YAML frontmatter. Drop a `.md` file into the appropriate folder and it shows up automatically:

```
content/
├── blog/       ← date-prefixed posts (2025-01-15-my-post.md)
└── docs/       ← reference pages (getting-started.md)
```

## Writing a Blog Post

Create a new `.md` file in `content/blog/` with this frontmatter:

```yaml
---
title: "Your Post Title"
date: 2025-02-14
summary: "A short description for the blog list."
tags: [topic1, topic2]
draft: false
---
```

Set `draft: true` to hide a post while you're still working on it.

## Writing a Doc Page

Doc pages go in `content/docs/`. The `order` field controls sidebar sorting:

```yaml
---
title: "Page Title"
order: 1
---
```

Lower numbers appear first in the sidebar.
