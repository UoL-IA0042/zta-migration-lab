# Observability Stack (tpi2-1)

Prometheus (90-day retention, covering the full experimental period),
Grafana, and Loki on tpi2-1; `prometheus-node-exporter` from the Ubuntu
archive on all four nodes. Deploy before Phase 1 — baseline measurements
depend on it, and instrumentation must precede experiments.

```bash
# vault grafana_admin_password first
ansible-playbook -i inventory.yaml site.yaml
```

- Grafana: http://10.0.0.71:3000 (datasources auto-provisioned)
- Prometheus: http://10.0.0.71:9090
- Loki: push logs from other components via Docker's loki logging
  driver or promtail if/when log aggregation is needed; node metrics
  alone cover the resilience and performance procedures.

Isolating this stack on tpi2-1 keeps measurement overhead off the
workload and gateway nodes (see Experimental Design).

Export Prometheus snapshots (`/api/v1/admin/tsdb/snapshot`) into the
data repository at the end of each phase.
