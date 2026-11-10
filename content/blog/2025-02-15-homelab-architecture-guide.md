---
title: "Homelab Architecture Guide — LXC and Docker on Proxmox"
date: 2025-02-15
summary: "A hybrid architecture guide for Proxmox using LXC containers for core infrastructure and a Docker VM for application stacks."
tags: [proxmox, docker, homelab]
image: /static/images/thumbnails/homelab-architecture-guide.svg
category: homelab
draft: false
---

This guide outlines a **Hybrid Architecture** for Proxmox, utilizing a mix of **LXC Containers** for core infrastructure and a **Docker VM** for application stacks. This ensures maximum stability and easy resource management.

---

## 1. Resource Allocation Overview

| **Proxmox Environment** | **Core Role**             | **CPU Cores** | **RAM** | **Storage** |
| ----------------------- | ------------------------- | ------------- | ------- | ----------- |
| **LXC 1**               | Pi-hole + Unbound         | 1 Core        | 512 MB  | 8 GB        |
| **Docker VM**           | App Stack (Ubuntu/Debian) | 2 Cores       | 8–12 GB | 100 GB+     |

## 2. Infrastructure Setup (LXCs)

Using LXCs for these services ensures your network "front door" and DNS remain active even if the main Docker VM is undergoing maintenance.

- **Pi-hole + Unbound:** Primary DNS. Configure Unbound to port `5335`.
    
- **Nginx Proxy Manager:** The entry point for all web traffic. Point your domain/subdomains to the IP of the Docker VM using specific ports.
    
- **Uptime Kuma:** Monitor all services (LXCs, VM, and external sites) independently.
    

---

## 3. Application Stack (Docker VM)

Create a single directory (e.g., `~/docker-stack`) and save the following as `docker-compose.yml`.

### Docker Compose Configuration

```yaml
services:
  # --- Management Tools ---
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: always
    security_opt:
      - no-new-privileges:true
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    ports:
      - 9443:9443

  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=86400

  # --- Personal Services ---
  mealie:
    image: ghcr.io/mealie-recipes/mealie:latest
    container_name: mealie
    restart: always
    environment:
      - TZ=America/New_York
      - ALLOW_REGISTRATION=true
    volumes:
      - mealie_data:/app/data
    ports:
      - 9000:9000

  calibre-web-auto:
    image: crocodilestick/calibre-web-automated:latest
    container_name: calibre-web-auto
    restart: unless-stopped
    environment:
      - TZ=America/New_York
      - PUID=1000
      - PGID=1000
    volumes:
      - calibre_config:/config
      - calibre_books:/books
      - calibre_import:/import
    ports:
      - 8083:8083

  bentopdf:
    image: bentopdf/bentopdf:latest
    container_name: bentopdf
    restart: unless-stopped
    ports:
      - 8080:8080

  # --- Infrastructure Sync ---
  nebula-sync:
    image: metebalci/nebula-sync:latest
    container_name: nebula-sync
    restart: unless-stopped
    environment:
      - TZ=America/New_York
      - NEBULA_MASTER_IP=192.168.1.XX # LXC 1 IP
      - NEBULA_MASTER_API_KEY=your_api_key
      - NEBULA_SLAVE_IP=192.168.1.YY  # Secondary DNS IP
      - NEBULA_SLAVE_API_KEY=your_api_key
      - NEBULA_SYNC_INTERVAL=300

volumes:
  portainer_data:
  mealie_data:
  calibre_config:
  calibre_books:
  calibre_import:
```

---

## 4. Hardware Optimization Checklist

### Proxmox Storage Settings

- **LVM-Thin:** Use this for your VM/LXC storage to enable fast snapshots.
    
- **Discard/TRIM:** In VM Hardware settings, set the SCSI Controller to `VirtIO SCSI Single` and check the **Discard** box on the Hard Disk.
    

### Host OS Performance

- **Edit fstab:** Add `noatime` to your SSD mount point in `/etc/fstab` to reduce unnecessary writes.
    
- **CPU Governor:** Ensure Proxmox is using the `performance` or `on-demand` governor:
    
    ```bash
    echo "performance" | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
    ```
    

### Networking Best Practice

- **Static IPs:** Assign static IPs to your Proxmox host, all LXCs, and the Docker VM within your router or via `/etc/network/interfaces`.
    
- **Reverse Proxy:** Only open ports `80` and `443` on your router, pointing to the **Nginx Proxy Manager LXC**. All other services should be accessed via subdomains (e.g., `mealie.yourdomain.com`).
