---
title: "Jellyfin and NAS Mount Recovery"
date: 2025-02-11
summary: "A recovery guide for when Jellyfin loses access to media after a server freeze causes SMB/CIFS mounts to drop."
tags: [self-hosted, jellyfin, nas, troubleshooting]
image: /static/images/thumbnails/jellyfin-nas-mount-recovery.svg
category: homelab
draft: false
---

# Recovery Guide: Jellyfin & NAS Mount Recovery

**Scenario:** The server froze due to CPU overload (heavy downloading/unpacking), causing the network shares (SMB/CIFS) to drop. Jellyfin cannot see media because the `/data` directory is empty or unmounted.

---

## 1. Prerequisites & Health Checks

Before attempting to remount, ensure the "source" and "tools" are ready.

### Check NAS Status

Ensure your Samba service is actually running in the NAS container/server. If the NAS is down, the mount will fail.

- **Action:** Log into your NAS and verify the Samba/SMB service status.
    

### Verify `cifs-utils`

Ensure the client VM has the necessary tools to handle SMB shares.

```bash
sudo apt update && sudo apt install cifs-utils -y
```

_Note: If it says "already the newest version," you are good to go._

---

## 2. Diagnostic: Check the `/data` Directory

Check if the media folders are currently visible on the VM.

```bash
cd /data
ls
```

- **Success:** You see `movies`, `shows`, and `downloads`.
    
- **Failure:** The directory is empty or missing folders. This confirms a **mounting issue**.
    

---

## 3. The Fix: Refreshing Mounts

If the folders are missing, you need to force the system to re-read the `/etc/fstab` configuration and remount the network drives.

### Step A: Reload the System Daemon

Tell Ubuntu to acknowledge any changes made to configuration files.

```bash
sudo systemctl daemon-reload
```

### Step B: Mount All File Systems

Force the system to mount everything defined in `/etc/fstab`.

```bash
sudo mount -a
```

### Step C: Verify Visibility

Check the directory again to ensure the network share is active.

```bash
ls /data
```

---

## 4. Restart Jellyfin

Once the files are visible to the OS, restart the Jellyfin container so it can re-index the media.

```bash
cd /docker/jellyfin/
docker compose restart jellyfin
```

---

## Key Notes for Troubleshooting

> [!IMPORTANT]
> 
> **Why did this happen?**
> 
> When the CPU overloaded, the cifs kernel client likely timed out. Because the `/etc/fstab` entry exists, the system knows where to go, but it needs the `mount -a` command to physically re-establish the connection after a hang.

- **Config Location:** `/etc/fstab` (Contains the IP and credentials for the NAS).
    
- **Verification File:** If you see `text.txt` in `/data` but not your media, double-check that the NAS didn't unmount the drive internally.
