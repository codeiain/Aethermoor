---
tags:
  - dashboards
  - grafana
---

# Grafana Service

**Port:** 5007 (host), 3000 (container)  
**Language:** Go (prebuilt image)

Grafana provides dashboards and visualization for all metrics and logs.

## Responsibilities

- Visualize metrics from Prometheus, logs from Loki
- Provide dashboards for service health, performance, and alerts
- User authentication for dashboard access

## Configuration
- Data volume: `/var/lib/grafana`
- Provisioning: `/etc/grafana/provisioning` (mount from host)

## Notes
- Web UI at `http://localhost:5007` (default admin/admin)
- Change default password after first login
