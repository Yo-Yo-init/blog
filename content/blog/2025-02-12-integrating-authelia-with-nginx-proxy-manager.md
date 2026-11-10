---
title: "Integrating Authelia with Nginx Proxy Manager"
date: 2025-02-12
summary: "A complete guide to setting up Authelia as an SSO authentication middleware for services behind Nginx Proxy Manager."
tags: [self-hosted, authelia, nginx, docker, security]
image: /static/images/thumbnails/integrating-authelia-with-nginx-proxy-manager.svg
category: homelab
draft: false
---

# Guide: Integrating Authelia with Nginx Proxy Manager

This guide documents the setup of **Authelia** as an authentication middleware for **Nginx Proxy Manager (NPM)**. It creates a "Single Sign-On" experience where users must log in before accessing internal services like Sonarr, Radarr, or Portainer.

## 1. Prerequisites & Network

We need a dedicated Docker network so NPM and Authelia can communicate securely.

```bash
docker network create npm_network
```

---

## 2. Directory Structure

Ensure your host directory at `/home/pepper/docker` looks like this. We are separating the Authelia config and the Nginx "snippets" (reusable code blocks).

```
/home/pepper/docker/
├── authelia/
│   ├── docker-compose.yml
│   ├── config/
│   │   ├── configuration.yml
│   │   └── users_database.yml
│   └── secrets/
│       ├── JWT_SECRET
│       ├── SESSION_SECRET
│       └── STORAGE_PASSWORD
└── snippets/            <-- Mounted into NPM container
    ├── authelia-location.conf
    ├── authelia-authrequest.conf
    ├── proxy.conf
    └── websocket.conf
```

---

## 3. Authelia Setup

### Step A: Generate Secrets

Run these commands to generate secure keys. This prevents sensitive data from being stored in plain text.

```bash
mkdir -p /home/pepper/docker/authelia/secrets
cd /home/pepper/docker/authelia/secrets

tr -cd '[:alnum:]' < /dev/urandom | fold -w 64 | head -n 1 > JWT_SECRET
tr -cd '[:alnum:]' < /dev/urandom | fold -w 64 | head -n 1 > SESSION_SECRET
tr -cd '[:alnum:]' < /dev/urandom | fold -w 64 | head -n 1 > STORAGE_PASSWORD
```

### Step B: Authelia `docker-compose.yml`

File: `/home/pepper/docker/authelia/docker-compose.yml`

```yaml
services:
  authelia:
    container_name: authelia
    image: authelia/authelia:latest
    restart: unless-stopped
    networks:
      - npm_network
    expose:
      - 9091
    volumes:
      - ./config:/config
      - ./secrets:/secrets
    environment:
      - TZ=America/New_York
      - AUTHELIA_IDENTITY_VALIDATION_RESET_PASSWORD_JWT_SECRET_FILE=/secrets/JWT_SECRET
      - AUTHELIA_SESSION_SECRET_FILE=/secrets/SESSION_SECRET
      - AUTHELIA_STORAGE_ENCRYPTION_KEY_FILE=/secrets/STORAGE_PASSWORD

networks:
  npm_network:
    external: true
```

### Step C: Users Database (`users_database.yml`)

File: `/home/pepper/docker/authelia/config/users_database.yml`

- **Note:** Passwords must be hashed using **Argon2id**.
    
- Tool: [Argon2.online](https://argon2.online/) (Settings: Iterations=3, Memory=65536, Parallelism=4).
    

```yaml
users:
  pepper:
    displayname: "Pepper"
    # Wrap hash in quotes!
    password: "$argon2id$v=19$m=65536,t=3,p=4$YOUR_HASH_HERE..." 
    email: pepper@yourdomain.com
    groups:
      - admins
```

### Step D: Main Configuration (`configuration.yml`)

File: `/home/pepper/docker/authelia/config/configuration.yml`

- **Fix Applied:** Removed `storage.encryption_key_file` (loaded via Env).
    
- **Fix Applied:** Updated `session` block to new format.
    
- **Fix Applied:** Set `default_redirection_url` to internal domain.
    

```yaml
server:
  address: 'tcp://:9091'
  endpoints:
    authz:
      auth-request:
        implementation: 'AuthRequest'

log:
  level: info

totp:
  issuer: authelia.com

authentication_backend:
  file:
    path: /config/users_database.yml

access_control:
  default_policy: deny
  rules:
    - domain: "auth.yourdomain.com"
      policy: bypass
    - domain: "*.yourdomain.com"
      policy: one_factor

session:
  name: authelia_session
  cookies:
    - domain: yourdomain.com
      authelia_url: https://auth.yourdomain.com
      default_redirection_url: https://auth.yourdomain.com
  expiration: 1h
  inactivity: 5m

storage:
  local:
    path: /config/db.sqlite3

notifier:
  filesystem:
    filename: /config/notification.txt
```

---

## 4. Nginx Proxy Manager (NPM) Setup

### Step A: NPM `docker-compose.yml`

Ensure your NPM compose file mounts the snippets volume and joins the network.

```yaml
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    # ... ports ...
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
      - /home/pepper/docker/snippets:/snippets  # CRITICAL MOUNT
    networks:
      - npm_network

networks:
  npm_network:
    external: true
```

### Step B: The Snippets

Create these files in `/home/pepper/docker/snippets/`.

**1. `authelia-location.conf`**

```nginx
set $upstream_authelia http://authelia:9091/api/authz/auth-request;

location /internal/authelia/authz {
    internal;
    proxy_pass $upstream_authelia;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header X-Original-URL $scheme://$http_host$request_uri;
    proxy_set_header X-Original-Method $request_method;
    proxy_set_header X-Forwarded-Method $request_method;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $http_host;
    proxy_set_header X-Forwarded-Uri $request_uri;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header Content-Length "";
    proxy_set_header Connection "";
}
```

**2. `authelia-authrequest.conf`**

- **Fix Applied:** Added `error_page 401` to force redirect to login portal.

```nginx
auth_request /internal/authelia/authz;
auth_request_set $target_url $scheme://$http_host$request_uri;
auth_request_set $user $upstream_http_remote_user;
auth_request_set $groups $upstream_http_remote_groups;
auth_request_set $name $upstream_http_remote_name;
auth_request_set $email $upstream_http_remote_email;
proxy_set_header Remote-User $user;
proxy_set_header Remote-Groups $groups;
proxy_set_header Remote-Name $name;
proxy_set_header Remote-Email $email;

# Redirect 401 errors to Authelia Login
error_page 401 =302 https://auth.yourdomain.com/?rd=$target_url;
```

**3. `proxy.conf`**

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Scheme $scheme;
proxy_set_header X-Forwarded-Proto  $scheme;
proxy_set_header X-Forwarded-For    $remote_addr;
proxy_set_header X-Real-IP          $remote_addr;
```

**4. `websocket.conf`**

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

---

## 5. Activation & Configuration

1. **Start Containers:**
    
    ```bash
    # Start Authelia
    cd /home/pepper/docker/authelia
    docker-compose up -d
    
    # Restart NPM to load snippets
    docker restart nginx-proxy-manager
    ```
    
2. **Expose Auth Portal (NPM GUI):**
    
    - **Host:** `auth.yourdomain.com`
        
    - **Forward:** `authelia` : `9091`
        
    - **SSL:** Force SSL enabled.
        
    - **Advanced:** **LEAVE BLANK** (Do not protect the login page).
        
3. **Protect a Service (e.g., Sonarr):**
    
    - **Host:** `sonarr.yourdomain.com`
        
    - **Forward:** (Standard Sonarr IP/Port).
        
    - **Advanced:** Paste this block:

```nginx
include /snippets/authelia-location.conf;

location / {
    include /snippets/authelia-authrequest.conf;
    include /snippets/proxy.conf;
    include /snippets/websocket.conf;
    
    # REQUIRED: Repeat destination IP here
    proxy_pass http://192.168.1.XX:8989; 
}
```

## 6. Verification

- **Success:** Visiting `sonarr.yourdomain.com` automatically redirects to `auth.yourdomain.com`.
    
- **Success:** Logging in redirects you back to Sonarr.
    
- **Troubleshooting:**
    
    - _401 Error (Text Only):_ Missing `error_page 401` line in `authelia-authrequest.conf`.
        
    - _500 Error:_ Check `docker logs authelia`. Usually a YAML indentation issue or invalid Secret file path.
        
    - _Redirect Loop:_ You accidentally added the snippets to the `auth.yourdomain.com` host itself.
