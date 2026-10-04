# Calico East-West Policies (Phase 2: workload-to-workload zero trust)

Exercises the east-west dimension: a three-tier app (frontend -> api ->
db) under default-deny with explicit allows mirroring the legitimate
call graph.

```bash
# 1. Redeploy K3s with flannel disabled (ansible-k3s README, Calico variant)
# 2. Install Calico:
CALICO_VERSION=v3.30.1 ./install-calico.sh      # VERIFY current version
# 3. Deploy workloads and policies:
kubectl apply -f workloads.yaml
kubectl apply -f policies/east-west.yaml
```

Test procedure (east-west analogue of the access matrix; run from a
debug pod, e.g. `kubectl run probe -n tier-frontend --rm -it
--image=busybox -- sh`):

| Probe | Expected |
|---|---|
| external -> frontend VIP :80 | allow |
| frontend -> api :80 | allow |
| api -> db :5432 | allow |
| frontend -> db :5432 | deny |
| external -> api / db | deny |
| db -> api (egress) | deny |

Record results as exec probes in a `matrix-phase2-calico.yaml` so they
land in the same CSV pipeline as the north-south phases.

Analysis note: compare the policy-authoring experience here (label
selectors over a call graph) with OpenZiti (service/dial policies) and
NetBird (group-to-resource rules) — three expressions of the same
least-privilege intent, which is the cross-implementation comparison
at the heart of RQ2/RQ5.
