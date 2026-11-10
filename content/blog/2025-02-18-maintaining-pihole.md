---
title: "Maintaining Pi-hole"
date: 2025-02-18
summary: "A quick cheatsheet for keeping your Pi-hole healthy — status checks, updates, and backups."
tags: [networking, pihole, dns]
image: /static/images/thumbnails/maintaining-pihole.svg
category: homelab
draft: false
---

## **Maintenance and Backup**

**Health check (from SSH)**

```bash
pihole status
```

```bash
systemctl status pihole-FTL --no-pager
```

**Update all pieces periodically (from SSH)** _— set a recurring monthly reminder!_

```bash
sudo pihole -up
```

```bash
sudo apt update && sudo apt full-upgrade -y
```

```bash
sudo systemctl restart unbound
```

**Export/Import configuration** (from Pi-hole Web UI) _when you make changes_

**Web UI → _Settings → Teleporter_** (and email yourself the backup)
