---
title: "Reverse proxy and auth"
order: 3
updated: 2026-11-22
---

Every web service I expose goes through Nginx Proxy Manager (NPM), and the ones that need a login go through Authelia first.

## Nginx Proxy Manager

NPM runs as a container from the `jc21/nginx-proxy-manager` image on the Docker VM. It publishes ports 80 and 443 for traffic and 81 for the admin UI. The Compose folder holds `data/`, `letsencrypt/` and a `snippets/` folder that I added for Authelia.

- Volumes: `./data:/data`, `./letsencrypt:/etc/letsencrypt` and `./snippets:/snippets`.
- Network: an external Docker network named `npm_network`. Authelia has to join the same one.

## Authelia

Authelia answers nginx's `auth_request` and passes the verified user to the backend as `Remote-User`, `Remote-Groups`, `Remote-Name` and `Remote-Email` headers. It listens on port 9091 inside the shared network, and the check endpoint is `http://authelia:9091/api/authz/auth-request`.

In its `configuration.yml` the `domain` setting and the cookie handling (`secure: true` or `false`) decide whether login works at all.

## The four snippets

Using NPM's Advanced tab switches off its default proxy headers, so the snippets put them back and add the auth check.

- `authelia-location.conf` defines an internal `location` that proxies to the Authelia check endpoint.
- `authelia-authrequest.conf` enforces the check and maps the response into the `Remote-*` headers.
- `proxy.conf` re-sets `Host`, `X-Forwarded-*` and `X-Real-IP`.
- `websocket.conf` adds the upgrade headers that some apps need for live updates.

In the Advanced tab of each protected proxy host:

```nginx
include /snippets/authelia-location.conf;

location / {
    include /snippets/authelia-authrequest.conf;
    include /snippets/proxy.conf;
    include /snippets/websocket.conf;
    proxy_pass http://<SERVICE_HOST>:<SERVICE_PORT>;
}
```

The `proxy_pass` line has to be edited by hand to the real host and port of the service. The full walkthrough is in [Protecting NPM Hosts with Authelia Snippets](/blog/protecting-npm-hosts-with-authelia/).

## When it breaks

- **500 error:** nginx cannot reach Authelia. Check the container name in `authelia-location.conf` and that both containers are on `npm_network`.
- **Login loop:** the `domain` in `configuration.yml` is wrong, or the cookie `secure` setting does not match how you reach the site.
- **Websockets failing:** the `websocket.conf` include is missing from the Advanced tab.

## Status

Draft. Taken from my working notes on the setup, which have not been reviewed yet.
