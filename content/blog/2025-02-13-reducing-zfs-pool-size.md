---
title: "Reducing ZFS Pool Size on Proxmox"
date: 2025-02-13
summary: "How to manually reduce a ZFS subvolume quota on Proxmox when pct resize fails."
tags: [proxmox, zfs, storage]
image: /static/images/thumbnails/reducing-zfs-pool-size.svg
category: homelab
draft: false
---

## 1. Find the ZFS Dataset Path

Use the `zfs list` command to find your container's dataset. Replace `114` with your container number:

```bash
zfs list | grep 114
```

The output will include a line similar to this, confirming the path:

```
NAME                           USED  AVAIL  REFER  MOUNTPOINT
Tank/subvol-114-disk-0          2.5T   500G   2.5T  /Tank/subvol-114-disk-0
```

## 2. Check the Mount Point on the Host

The ZFS subvolume is actually mounted directly on the Proxmox host, usually at a path that matches the ZFS path:

```bash
mount | grep subvol-114-disk-0
```

## 3. Reducing the Size

Since the `pct resize` command failed, proceed with the manual method using the path **`Tank/subvol-114-disk-0`**:

1. **Stop the Container:** `pct stop 114`
    
2. **Manually Set Quota:** `zfs set refquota=1800G Tank/subvol-114-disk-0`
    
3. **Update Config File:** Edit `/etc/pve/lxc/114.conf` to change `size=2900G` to `size=1800G`.
    
4. **Start Container:** `pct start 114`

> **Note:** I was having issues earlier by specifying `1.8T` instead of using `1800G` for the disk size parameter. Your mileage may vary depending on Proxmox version.
