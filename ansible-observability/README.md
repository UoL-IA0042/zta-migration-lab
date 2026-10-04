# Observability Stack (tpi2-1)

Prometheus (90-day retention, covering the full experimental period),
Grafana, and Loki on tpi2-1; `prometheus-node-exporter` from the Ubuntu
archive and Grafana Alloy (log agent, Grafana apt repository) on all
four nodes. Deploy before Phase 1 — baseline measurements
depend on it, and instrumentation must precede experiments.

```bash
# vault grafana_admin_password first
ansible-playbook -i inventory.yaml site.yaml
```

- Grafana: http://10.0.0.71:3000 (datasources auto-provisioned)
- Prometheus: http://10.0.0.71:9090
- Loki: http://10.0.0.71:3100, fed by Alloy on every node.

## Log shipping (Alloy)

Alloy replaces Promtail, which is deprecated. Each node ships:

- the systemd journal (`job="journal"`, labels `unit`, `level`): system
  services, node_exporter, OpenVPN, K3s, kernel;
- Docker container logs (`job="docker"`, labels `container`,
  `compose_project`, `compose_service`).

Every stream carries `host="tpi2-N"`, so `{host="tpi2-3"}` in Grafana
Explore returns one node's logs. The playbook ends by checking that Loki
has received logs from all four hosts.

- **Deployment order.** Observability deploys first, before Docker exists
  on most nodes. The play pre-creates the `docker` group and adds `alloy`
  to it; Docker discovery retries until a later component installs
  docker.io, so no re-run is needed.
- **Permissions.** Membership of `docker` is root-equivalent. Set
  `alloy_collect_docker: false` to ship the journal only.
- **Not collected.** K3s pod logs (`/var/log/pods`, containerd) in the
  Phase 2 Calico experiments; add a `loki.source.file` block if needed.
- **Overhead.** Alloy runs on every node in every phase, like
  node_exporter, so its overhead is constant across experiments.
- **VERIFY.** `alloy_version` pins the 1.x series; record the resolved
  version (`dpkg -s alloy | grep Version`) in the journal at deploy time.

Isolating this stack on tpi2-1 keeps measurement overhead off the
workload and gateway nodes (see Experimental Design).

Export Prometheus snapshots (`/api/v1/admin/tsdb/snapshot`) into the
data repository at the end of each phase.
