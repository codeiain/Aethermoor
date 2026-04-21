---
tags:
  - dashboard
  - homepage
---

# Homepage Service
**Port:** 8888 (host), 3000 (container)  
**Language:** Node.js / React (prebuilt image)

Self-hosted dashboard for links, widgets, and service status. Used for quick access to all internal tools and monitoring.

## Responsibilities

- Display customizable dashboard with links and widgets
- Show status of internal services (Grafana, Prometheus, etc.)
- Allow configuration via mounted `/app/config` volume

## Configuration
- Mount your dashboard config folder to `/app/config` in the container.
- Example: `- ./homepage/:/app/config`

## Notes
- Depends on other services for status widgets (Grafana, Prometheus, Loki, etc.)
- Not security-hardened; restrict to internal network.
