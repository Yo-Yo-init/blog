# Hosting Guide — Proxmox Self-Hosted Deployment (VPN-Only Access)

> Step-by-step instructions for provisioning a VM on Proxmox and deploying the blog as an internal service accessible only via NetBird VPN.

---

## 1. VM Provisioning in Proxmox

### Create the VM

1. Open the Proxmox web UI (`https://<proxmox-ip>:8006`).
2. Click **Create VM** and configure:

| Setting        | Value                                          |
| -------------- | ---------------------------------------------- |
| **VM ID**      | Pick an available ID (e.g., `200`)             |
| **Name**       | `blog-server`                                  |
| **OS ISO**     | Upload your chosen ISO (see §2) to `local`     |
| **Machine**    | `q35`                                          |
| **BIOS**       | `OVMF (UEFI)` or `SeaBIOS` — either works     |

### Resource Allocation

This is a lightweight Python web app — keep it lean:

| Resource   | Recommended | Minimum |
| ---------- | ----------- | ------- |
| **CPU**    | 2 cores     | 1 core  |
| **RAM**    | 2 GB        | 1 GB    |
| **Disk**   | 16 GB       | 8 GB    |
| **NIC**    | `virtio` (bridged to your LAN, e.g., `vmbr0`) | — |

> [!TIP]
> Enable **Ballooning** for RAM so Proxmox can reclaim unused memory from this VM for other workloads.

### Storage

- Use `virtio-scsi` or `VirtIO Block` for best I/O performance.
- Thin provisioning is fine for a blog — disk usage will be minimal.

---

## 2. Operating System

### Recommended: Debian 12 (Bookworm) — Minimal Server

| Why Debian?                                |
| ------------------------------------------ |
| Extremely stable, long support cycle       |
| Minimal footprint out of the box           |
| Large package ecosystem                    |
| `qemu-guest-agent` support built-in        |
| Familiar `apt` package manager             |

### Installation Notes

- Choose **minimal / no desktop** during install.
- Set a strong root password; create a non-root user (e.g., `deploy`).
- Enable **SSH server** during setup.
- After install, install the guest agent:

```bash
sudo apt update && sudo apt install -y qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent
```

---

## 3. Initial Setup

Run all commands as your non-root user with `sudo`.

### 3.1 Updates

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades   # enable automatic security updates
```

### 3.2 SSH Access

Copy your public key from your Mac:

```bash
# Run this from your Mac
ssh-copy-id deploy@<vm-ip>
```

> [!NOTE]
> Since the VM is only reachable through your NetBird VPN, aggressive SSH hardening (disabling password auth, Fail2Ban, etc.) is optional. The VPN itself is the access control layer.

---

## 4. Install Dependencies

```bash
sudo apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  git \
  curl
```

### Python Application Setup

```bash
# Clone or copy project to the server
mkdir -p /opt/blog
cd /opt/blog
# (scp, rsync, or git clone your project here)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

---

## 5. Run the App as a Service

Since the blog is only accessed over VPN, Uvicorn can serve the app directly — no reverse proxy needed.

### Systemd Unit

Create `/etc/systemd/system/blog.service`:

```ini
[Unit]
Description=Blog (FastAPI + Uvicorn)
After=network.target

[Service]
User=deploy
Group=deploy
WorkingDirectory=/opt/blog
ExecStart=/opt/blog/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5
Environment="PATH=/opt/blog/venv/bin"

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now blog
sudo systemctl status blog
```

> [!TIP]
> Access the blog from any NetBird-connected device at `http://<vm-lan-ip>:8000`.

---

## 7. Maintenance Checklist

| Task                         | Frequency  | Command / Action                        |
| ---------------------------- | ---------- | --------------------------------------- |
| System updates               | Automatic  | `unattended-upgrades` handles this      |
| Check service status         | As needed  | `sudo systemctl status blog`            |
| View app logs                | As needed  | `sudo journalctl -u blog -f`           |
| Backup content               | Weekly     | `rsync` the `content/` folder off-site  |
| Proxmox VM snapshot          | Before major changes | Proxmox UI → VM → Snapshots   |

---

## Quick Reference — Full Command Sequence

```bash
# 1. System setup
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git qemu-guest-agent curl unattended-upgrades

# 2. App
mkdir -p /opt/blog && cd /opt/blog
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Service
sudo systemctl daemon-reload
sudo systemctl enable --now blog
```
