---
title: "Configuring Split DNS on Netbird"
date: 2025-02-19
summary: "A step-by-step guide to configuring Split DNS on Netbird so your local domains resolve correctly over a VPN tunnel."
tags: [networking, netbird, dns, vpn]
image: /static/images/thumbnails/configuring-split-dns-on-netbird.svg
category: homelab
draft: false
---

Here is the refined, step-by-step guide to making your local domains work remotely over Netbird.

### **The Goal**

We will configure **Split DNS**. This tells Netbird: _"When I try to access `anything.mydomain.com`, do not ask the public internet (Google). Instead, send that question through the VPN tunnel to my home Pi-hole."_

---

### **Prerequisites**

1. **Netbird Admin Access:** You need access to the [Netbird Dashboard](https://app.netbird.io/).
    
2. **Local DNS Server IP:** You need the internal IP address of your Pi-hole (e.g., `192.168.1.x`).
    
3. **Netbird Client:** The device you are connecting _from_ (e.g., your laptop or phone) must have the Netbird app installed and connected.
    

---

### **Step 1: Identify your DNS Server IP**

First, determine which IP address Netbird should target.

- If you have **Subnet Routes** enabled in Netbird (meaning you can already ping `192.168.1.x` addresses remotely), use your Pi-hole's **Local LAN IP** (e.g., `192.168.1.x`).
    
- _If you do not have subnet routes, you must install the Netbird client on your Pi-hole host and use its specific **Netbird IP** (e.g., `100.x.x.x`)._
    

**Recommendation:** Since you can already access services via IPv4, use the **Local LAN IP**.

### **Step 2: Add the Nameserver in Netbird**

1. Log in to the **[Netbird Admin Panel](https://app.netbird.io/)**.
    
2. Navigate to the **DNS** tab in the left sidebar.
    
3. Click the **Add Nameserver** button.
    

### **Step 3: Configure the Nameserver**

Fill in the popup form with the following details:

- **Name:** Give it a recognizable name (e.g., `Home Pi-hole`).
    
- **Description:** (Optional) "Resolves internal homelab domains."
    
- **Nameserver IP:** Enter the IP from Step 1 (e.g., `192.168.1.x`).
    
- **Port:** Leave this as `53` (unless you changed your Pi-hole port).
    
- **Distribution Groups:** Select **All** (or the specific group containing your remote devices).
    

**The Critical Part:**

- **Match Domains:** Enter your root domain name.
    
    - _Example:_ If your services are `jellyfin.batman.com` and `grafana.batman.com`, just enter **`batman.com`**.
        
    - _Do not_ add subdomains. This one entry covers everything.
        

Click **Save**.

### **Step 4: Refresh the Client**

DNS settings can take a moment to propagate.

1. On your remote device (Laptop/Phone), open the Netbird app.
    
2. **Disconnect** and **Reconnect**.
    
3. Wait about 10-15 seconds.
    

---

### **Step 5: Verification (Do this before opening the browser)**

Before you try to load the dashboard, check if your computer is actually finding the address.

On Windows:

Open Command Prompt or PowerShell and type:

```
nslookup jellyfin.yourdomain.com
```

On Mac/Linux:

Open Terminal and type:

```
nslookup jellyfin.yourdomain.com
```

**What to look for:**

- **Server:** Should be the IP of your Pi-hole (or a Netbird relay address).
    
- **Address:** This MUST return your local LAN IP (e.g., `192.168.1.12`).
    
    - _If it says "Non-existent domain" or returns a public internet IP, the settings haven't applied yet._
        

---

### **Step 6: The Result**

Once `nslookup` returns the correct local IP:

1. Open your browser.
    
2. Type `https://jellyfin.yourdomain.com`.
    
3. **Success:**
    
    - The request goes through Netbird.
        
    - Nginx Proxy Manager receives the **Domain Name**.
        
    - **Authelia works** because the domain matches the cookie.
        
    - You are logged in securely.
