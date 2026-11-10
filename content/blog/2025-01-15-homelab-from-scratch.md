---
title: "Building a Home Lab From Scratch"
date: 2025-01-15
summary: "A walkthrough of my Proxmox-based home lab setup — from hardware selection to VM provisioning."
tags: [homelab, proxmox, networking]
image: /static/images/thumbnails/homelab-from-scratch.svg
category: homelab
draft: false
---

Setting up a home lab is one of the best investments you can make for learning IT and cybersecurity hands-on. Here's how I built mine.

## Hardware

I'm running a Dell OptiPlex Micro with a quad-core i5, 32 GB RAM, and a 1 TB NVMe drive. Small, quiet, and power-efficient — perfect for 24/7 operation.

## Proxmox Setup

After flashing the Proxmox ISO to a USB drive, installation takes about 10 minutes. The web UI is immediately available at `https://<ip>:8006`.

```bash
# Post-install: remove the enterprise repo nag
sed -i 's/^deb/#deb/' /etc/apt/sources.list.d/pve-enterprise.list

# Add the no-subscription repo
echo "deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription" \
  > /etc/apt/sources.list.d/pve-no-sub.list

apt update && apt full-upgrade -y
```

## First VMs

I started with three VMs:

- **pfSense** — firewall and router for VLAN segmentation
- **Debian** — general-purpose server for Docker containers
- **Kali Linux** — dedicated penetration testing environment

## Network Segmentation

Using VLANs keeps lab traffic isolated from the home network:

| VLAN | Purpose         | Subnet          |
|------|-----------------|-----------------|
| 10   | Management      | 10.0.10.0/24    |
| 20   | Servers         | 10.0.20.0/24    |
| 30   | Lab / Pentest   | 10.0.30.0/24    |

## What's Next

In upcoming posts I'll cover setting up WireGuard for remote access, deploying a SIEM with Wazuh, and automating VM provisioning with Terraform.
