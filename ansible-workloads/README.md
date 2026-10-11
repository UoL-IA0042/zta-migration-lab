# Protected Workloads (tpi2-3)

The resources every remote-access architecture must protect:

| Service | Port | Matrix resource | Notes |
|---|---|---|---|
| PostgreSQL 16 | 5432 | `postgres` | per-role users; grants = intended least privilege |
| nginx intranet | 8080 | `intranet-web` | static internal app |
| Samba share | 445 | `file-service` | single credentialed share |
| socat echo | 8023 | `legacy-service` | deliberately unauthenticated cleartext |
| iperf3 server | 5201 | — (perf-battery target) | `lab-iperf3.service`; not part of the access model |

```bash
# vault all CHANGE-ME values first
ansible-playbook -i inventory.yaml site.yaml
```

Design notes:

- DB grants are the application-layer ground truth: admin/developer
  read+write, analyst read-only, contractor nothing. In Phase 1 the
  network lets a contractor *reach* postgres (perimeter over-breadth)
  but the database refuses the login (CONNECT is granted only to the
  other roles; init.sql runs only on an empty data directory, so this
  needs a clean rebuild of tpi2-3); in ZTNA phases the network itself denies —
  the matrix records both layers' behavior.
- The legacy service exists to exercise the segment-and-proxy pattern
  for RBAC-incapable systems (Experimental Design, resource
  determination phase).
- `init.sql` runs only on first database initialization; changing
  roles/grants requires wiping `pgdata` (clean re-deploy is the
  intended workflow).
- VERIFY: `dperson/samba` image on ARM64; substitute
  `ghcr.io/servercontainers/samba` if it fails on the RK1.
