---
title: "Network and DNS"
order: 2
updated: 2026-11-22
---

How names resolve at home and away from home, and what keeps the DNS service healthy.

## Pi-hole

Pi-hole is my DNS filter and the resolver for local names. It runs on its own host, reachable over SSH, with `pihole-FTL` as the systemd service. A second Pi-hole runs in a separate LXC guest.

Monthly routine:

```bash
pihole status
systemctl status pihole-FTL --no-pager
sudo pihole -up
sudo apt update && sudo apt full-upgrade -y
sudo systemctl restart unbound
```

The `unbound` step suggests it sits behind Pi-hole as the upstream resolver, but I have not written that setup down yet. For configuration backups I export from Settings, then Teleporter, in the web UI after every change. The longer version is in [Maintaining Pi-hole](/blog/maintaining-pihole/).

## Remote access with NetBird

NetBird is the VPN for getting home from elsewhere. Settings live in its admin panel. Two things matter for DNS:

- **Subnet routes.** With them on, remote devices reach LAN addresses directly. Without them, each service host needs its own NetBird client and is reached by its NetBird address.
- **Distribution groups.** Nameserver settings are pushed per group. I use the group that contains my remote devices.

## Split DNS

Split DNS makes my internal names resolve over the tunnel while everything else goes to the normal public resolver.

1. In the NetBird admin panel open the DNS tab and add a nameserver.
2. Point it at the Pi-hole address on port 53. I use the LAN address because subnet routes are on.
3. Set Match Domains to the root domain only, for example `example.lab`. One entry covers every subdomain, so adding them one by one is wrong.
4. Disconnect and reconnect the NetBird app on the client, then wait 10 to 15 seconds.

To verify before opening a browser, run `nslookup jellyfin.example.lab`. The server in the answer should be the Pi-hole (or a NetBird relay), and the address should be the LAN address of the proxy. The step by step version is in [Configuring Split DNS on NetBird](/blog/configuring-split-dns-on-netbird/).

## Status

Draft. Based on my notes and the two posts linked above. The domain here is a placeholder.
