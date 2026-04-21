---
tags:
  - logs
  - loki
---

# Loki Service
**Port:** 3110 (host), 3100 (container)  
**Language:** Go (prebuilt image)

Grafana Loki log aggregation service. Collects and indexes logs from all containers for querying and visualization in Grafana.

## Responsibilities

- Aggregate logs from all Docker containers
- Store and index logs for search and analysis
- Integrate with Promtail for log shipping
- Provide log data to Grafana dashboards

## Configuration
- Config file: `/etc/loki/local-config.yaml` (mount from host)
- Data volume: `/loki`

## Notes
- Exposes HTTP API for log queries (default: `http://localhost:3110`)
- Used by Promtail and Grafana for log visualization.
