---
title: "Fixing Network Issues After a Proxmox Physical Migration"
date: 2025-02-14
summary: "When you move a Proxmox boot drive to new hardware, the network interface names change and the bridge breaks. Here's how to fix it."
tags: [proxmox, networking, troubleshooting]
image: /static/images/thumbnails/fixing-network-issues-proxmox-migration.svg
category: homelab
draft: false
---

When you move a Proxmox boot drive to a new server, the physical "path" to your network card changes. Because Proxmox uses **Predictable Network Interface Names**, the old name (e.g., `enp3s0`) likely doesn't exist on the new motherboard, causing the bridge to fail and leaving you with no Web GUI access.

Here is a step-by-step guide to fixing your `/etc/network/interfaces` file from the local console.

---

## Phase 1: Identify the New Hardware

Before editing the file, you must find out what the new server calls its network ports.

1. **List all interfaces:**
    
    ```bash
    ip link show
    ```
    
2. **Find the "Up" interface:** Look for an entry starting with `en...` (e.g., `enp0s31f6` or `eno1`).
    
    - **Tip:** If the cable is plugged in, that interface should say `LOWER_UP`.
        
    - **Note:** Ignore `lo` (loopback) and `vmbr0` (the bridge).
        
3. **Write down the name exactly.** (Watch out for `6` vs `s` or `0` vs `o`).
    

---

## Phase 2: Edit the Configuration

Use the `nano` text editor to map the old configuration to the new hardware name.

1. **Open the file:**
    
    ```bash
    nano /etc/network/interfaces
    ```
    
2. **Update the Physical Interface:** Look for the line that defines the physical port. It usually looks like this:
    
    ```
    iface OLD_NAME inet manual
    ```
    
    Change `OLD_NAME` to your **New Name** found in Phase 1.
    
3. **Update the Bridge Ports:** Look for the `vmbr0` section and find the `bridge-ports` line.
    
    ```
    auto vmbr0
    iface vmbr0 inet static
        address 192.168.1.100/24
        gateway 192.168.1.1
        bridge-ports OLD_NAME
        bridge-stp off
        bridge-fd 0
    ```
    
    Change `OLD_NAME` to your **New Name** here as well.
    

---

## Phase 3: A "Clean" Configuration Template

If your file is messy, here is what a standard, clean Proxmox single-NIC configuration should look like. You can use this as a template:

```
# Loopback interface
auto lo
iface lo inet loopback

# The physical interface (No IP assigned here!)
iface enp0s31f6 inet manual

# The virtual bridge (This is where your IP goes)
auto vmbr0
iface vmbr0 inet static
        address 192.168.1.100/24
        gateway 192.168.1.1
        bridge-ports enp0s31f6
        bridge-stp off
        bridge-fd 0
```

---

## Phase 4: Apply and Test

1. **Save and Exit:** Press `Ctrl + O`, then `Enter`, then `Ctrl + X`.
    
2. **Apply the changes:**
    
    ```bash
    ifreload -a
    ```
    
    _If `ifreload` is not found, use `systemctl restart networking`._
    
3. **Verify the Bridge:**
    
    ```bash
    ip addr show vmbr0
    ```
    
    Ensure it shows the correct IP and says `state UP`.
    
4. **Test Connectivity:**
    
    ```bash
    ping -c 3 8.8.8.8
    ```
    

---

## Troubleshooting Common Issues

| **Issue** | **Cause** | **Fix** |
|---|---|---|
| **"Device not found"** | Typo in the name | Re-run `ip link` and check for `6` vs `s`. |
| **State "UNKNOWN"** | Bridge has no ports | Ensure `bridge-ports` name matches the physical `iface` name exactly. |
| **No Ping to Router** | Wrong Gateway | Double check the `gateway` line matches your router's IP. |
| **Multiple NICs** | Plugged into wrong port | Move the ethernet cable to the other physical port or update the config to the other `en...` name. |

---

### Pro-Tip: The "Master" Reset

If you get completely stuck and cannot get the network up, you can temporarily assign an IP directly to the physical card just to get into the shell or download tools:

```bash
ip addr add 192.168.1.100/24 dev enp0s31f6
ip link set enp0s31f6 up
ip route add default via 192.168.1.1
```
