---
tags:
  - metrics
  - cadvisor
---

# cAdvisor Service
**Port:** 8080  
**Language:** Go (prebuilt image)

cAdvisor provides container metrics (CPU, memory, filesystem, network) for all running Docker containers.

## Responsibilities

- Collect and expose real-time resource usage for containers
- Integrate with Prometheus for metrics scraping
- Support Grafana dashboards for resource monitoring

## Configuration
- Requires access to Docker and system filesystems

## Notes
- Web UI at `http://localhost:8080`
- Used by Prometheus and Grafana for resource dashboards
