---
tags: 
  - logs 
  - promtail
---
# Promtail Service

**Port:** (none exposed)  
**Language:** Go (prebuilt image)

Promtail ships logs from Docker containers to Loki for aggregation and search.

## Responsibilities

- Collect logs from Docker containers
- Ship logs to Loki for indexing
- Support log filtering and relabeling

## Configuration
- Config file: `/etc/promtail/config.yml` (mount from host)
- Requires access to Docker socket and container logs

## Notes
- No web UI or API; runs as a background agent
- Used by Loki and Grafana for log aggregation
