---
title: "Backups"
order: 4
updated: 2026-11-22
---

What is backed up, how, and where the gaps are. I would rather publish the gaps than pretend there are none.

## Hypervisor guests

A weekly Proxmox backup job covers the Docker VM and the control container. It runs in snapshot mode with ZSTD compression and writes to a directory storage on a quota-limited dataset on the main ZFS pool.

Snapshots and restores on the hypervisor are always done by hand, by me. The AI agents have no access to it, on purpose.

## Known gap: no off-box copy

The backups sit on the same ZFS pool as the disks they protect. Losing that pool would lose both. I plan to fix it with either Proxmox Backup Server or a USB disk, and have not done it yet.

## The media host

It is a physical machine, so the Proxmox job does not cover it. Its app configs need their own backup, and I take a tarball of them before every big upgrade.

## Application backups

- **Pi-hole:** a Teleporter export from the web UI after every change.
- **Homepage dashboard:** a tarball of its config folder before each change. Secrets live in a separate env file that stays out of the YAML.
- **Everything else:** nothing separate yet. The VM backup is the only copy.

## Before an upgrade

1. Check that the latest backup of the host in question is recent.
2. Snapshot the VM, or tar the configs on the physical host.
3. Upgrade, then reboot if a kernel changed.

## Status

Draft. Unattended upgrades are something I want but have not confirmed are switched on, so I do not list them here.
