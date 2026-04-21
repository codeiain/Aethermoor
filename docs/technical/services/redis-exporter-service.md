---
tags: 
  - redis 
  - metrics
---
# Redis Exporter Service

**Port:** 9121  
**Language:** Go (prebuilt image)

Exports Redis metrics in Prometheus format for monitoring and alerting.

## Responsibilities

- Collect Redis server metrics (memory, ops/sec, clients, etc.)
- Expose metrics endpoint for Prometheus scraping

## Configuration
- Set `REDIS_ADDR` and `REDIS_PASSWORD` environment variables

## Notes
- Used by Prometheus and Grafana for Redis monitoring
- No web UI; metrics available at `http://localhost:9121/metrics`
