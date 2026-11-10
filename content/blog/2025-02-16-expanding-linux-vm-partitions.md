---
title: "Expanding Linux VM Partitions"
date: 2025-02-16
summary: "A guide to expanding Linux VM disk partitions in Proxmox — covering growpart, ext4, XFS, and LVM."
tags: [linux, proxmox, storage]
image: /static/images/thumbnails/expanding-linux-vm-partitions.svg
category: homelab
draft: false
---

# Guide: Expanding Linux VM Partitions (Proxmox)

This guide assumes you have already increased the disk size in the **Proxmox Web UI** and now need to reflect those changes within the Ubuntu guest OS.

## 1. Initial Verification

First, confirm that the kernel sees the new "physical" space.

```bash
# List all block devices
lsblk
```

- **What to look for:** Does `sda` show 150G while `sda2` still shows 49G?
    
- If it doesn't see 150G: Run this to force a rescan:
    
    ```bash
    echo 1 | sudo tee /sys/class/block/sda/device/rescan
    ```

---

## 2. Expand the Partition (The "Fence")

A disk is the "land," and a partition is the "fence." We need to move the fence to the edge of the new land.

### Install the Utility

If you don't have `growpart`, install it (you may need to delete some logs first if you are at 100%):

```bash
sudo apt update && sudo apt install cloud-guest-utils -y
```

### Run Growpart

```bash
# Syntax: sudo growpart /dev/[disk_name] [partition_number]
sudo growpart /dev/sda 2
```

---

## 3. Expand the Filesystem (The "House")

Now that the fence is moved, we tell the filesystem to occupy the new space.

### For EXT4 (Most Common)

```bash
sudo resize2fs /dev/sda2
```

### For XFS

```bash
sudo xfs_growfs /
```

---

## 4. Special Case: LVM (Logical Volume Manager)

If your `df -h` shows a path like `/dev/mapper/ubuntu--vg-ubuntu--lv`, your Ubuntu installation uses LVM. You have extra layers to expand.

1. **Resize Physical Volume (PV):**
    
    ```bash
    sudo pvresize /dev/sda2
    ```
    
2. **Extend Logical Volume (LV):**
    
    ```bash
    sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
    ```
    
3. **Resize the Filesystem:**
    
    ```bash
    sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
    ```

---

## 5. Final Confirmation

Verify that your root partition now reflects the new size.

```bash
df -h
```

> [!TIP]
> 
> Post-Expansion: Once space is available, restart your Docker containers. Jellyfin should now start successfully since the 2GiB "safety check" will pass.
> 
> ```bash
> docker start jellyfin
> ```
