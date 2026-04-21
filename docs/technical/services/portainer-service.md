---
tags:
  - docker
  - management
---

# Portainer Service
**Port:** 9900 (host), 9000 (container)  
**Language:** Go (prebuilt image)

Docker management UI for monitoring, managing, and troubleshooting containers and volumes.

## Responsibilities

- Visual management of Docker containers, images, and volumes
- View logs, stats, and resource usage
- Manage Docker networks and stacks
- User authentication for dashboard access

## Configuration
- Mount Docker socket: `/var/run/docker.sock:/var/run/docker.sock`
- Data volume: `portainer_data:/data`

## Notes
- Exposes a web UI on the host (default: `http://localhost:9900`)
- Change default admin password after first login.
