# Bare-Metal K3s Cluster: Turing Pi 2 (4x RK1, Ubuntu ARM64)

K3s cluster with cloud-analogous services:

| Cloud capability | Bare-metal analogue here |
|---|---|
| ELB/NLB (`LoadBalancer` services) | MetalLB in L2 mode, VIP pool on the lab LAN |
| EBS (replicated block volumes) | Longhorn across the per-node 4TB NVMe drives |

Topology: `tpi2-2` control plane; `tpi2-1`, `tpi2-3`, `tpi2-4` agents.
K3s ServiceLB is disabled in favor of MetalLB; Longhorn replaces
`local-path` as the default StorageClass (replica count 2).

## Files

- `requirements.yaml` — pinned collections
- `inventory.yaml` — cluster topology
- `group_vars/all.yaml` — versions, token, MetalLB pool, NVMe/Longhorn config
- `site.yaml` — four plays: node prep, server, agents, addons
- `templates/metallb-pool.yaml.j2` — IPAddressPool + L2Advertisement

## Usage

```bash
ansible-galaxy install -r requirements.yaml
# set k3s_token in group_vars/all.yaml via ansible-vault first
ansible-playbook -i inventory.yaml site.yaml
```

Verify:

```bash
kubectl get nodes -o wide
kubectl -n longhorn-system get pods
kubectl create deploy nginx --image=nginx && \
  kubectl expose deploy nginx --port 80 --type LoadBalancer
kubectl get svc nginx   # EXTERNAL-IP comes from the MetalLB pool
```

## Before first run

1. Generate a join token (`openssl rand -hex 32`) and vault-encrypt it as
   `k3s_token`.
2. Confirm `metallb_pool_range` is outside your DHCP scope.
3. `nvme_device` is formatted only if it carries no filesystem; existing
   data is never overwritten. Confirm each node sees its SSD at
   `/dev/nvme0n1` (`lsblk`) — slot-to-node PCIe mapping on the Turing Pi 2
   is not uniform.

## Calico experiment variant

For the Phase 2 Calico work, K3s must come up without flannel. In
`group_vars/all.yaml` extend the server args:

```
k3s_server_extra_args: >-
  --disable servicelb
  --write-kubeconfig-mode 640
  --flannel-backend=none
  --disable-network-policy
```

then install Calico (ARM64 supported) per the Tigera docs before nodes
report Ready. Re-flash and redeploy rather than converting a running
cluster, per the reproducibility procedure.

## Version pins (verified current 2026-08)

- K3s `v1.36.4+k3s1`
- MetalLB `v0.16.1`
- Longhorn `v1.12.1` (requires `open-iscsi`; installed by the prep play)
