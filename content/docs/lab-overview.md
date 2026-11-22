---
title: "Lab overview"
order: 1
updated: 2026-11-22
---

This is the map of my homelab: what runs where, and which page to read for the detail. The pages in this section are reference notes, not tutorials. When something is worth a full write-up it goes on the [blog](/blog/) instead.

## The hosts

- **Hypervisor.** One Proxmox node. It hosts a small number of guests and holds a ZFS pool that backs most of the storage.
- **Docker VM.** A VM on that node running Ubuntu with Docker and Compose. Most of my self-hosted apps live here as Compose stacks, including the reverse proxy, the login gate and the dashboard.
- **Media host.** A separate physical machine, not a Proxmox guest. It runs its own Docker and gets its own upgrades.
- **LXC guests.** A couple of containers on the hypervisor, one for the media share and one for a second DNS server.
- **Control container.** An LXC guest that runs my AI agents. The [Hermes series](/blog/self-hosted-ai-agent-team-with-hermes/) covers it.

## Services by job

- **DNS:** Pi-hole for blocking and local names. See [Network and DNS](/docs/network-and-dns/).
- **Remote access:** NetBird, with split DNS so my internal names resolve away from home. Same page.
- **Front door:** Nginx Proxy Manager, with Authelia as the login gate. See [Reverse proxy and auth](/docs/reverse-proxy-and-auth/).
- **Dashboard and monitoring:** a Homepage dashboard, plus Uptime Kuma and Dozzle for status and logs.
- **Media:** Jellyfin.
- **Misc tools:** Mealie, n8n and Stirling PDF.

## How I run changes

Nothing gets upgraded without a backup first. Snapshots and restores of the hypervisor are always a manual job done by me. See [Backups](/docs/backups/) for what is covered and what is not.

## About these pages

Status: draft. They are written from my internal lab notes, which I have not yet re-checked line by line. I leave out addresses, real domains and anything secret on purpose, so a few details are generic.
