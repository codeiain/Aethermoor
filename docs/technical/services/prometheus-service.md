---
tags: 
  - metrics 
  - prometheus
---

# Prometheus Service

**Port:** 9090  
**Language:** Go (prebuilt image)

Prometheus collects and stores time-series metrics from all services for monitoring and alerting.

## Responsibilities

- Scrape metrics from all instrumented services
- Store time-series data for querying and alerting
- Integrate with Grafana for dashboards

## Configuration
- Config file: `/etc/prometheus/prometheus.yml` (mount from host)
- Data volume: `/prometheus`

## Notes
- Web UI at `http://localhost:9090`
- Used by Grafana for metrics visualization
