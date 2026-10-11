# AWS Environment (Terraform)

VPC (10.100.0.0/16), Graviton EC2 instances (ARM64 parity with the RK1
nodes), S3 data bucket, and per-role IAM users whose policies encode the
intended cloud access model.

| Resource | Matrix mapping |
|---|---|
| `aws_instance.app` (10.100.10.10:8080) | `aws-app` |
| `aws_s3_bucket.data` | `aws-s3-data` |
| IAM users remote-* | probing credentials (AWS profiles) |
| `aws_instance.vpn_gateway` | Phase 1 site-to-site terminator |
| `aws_instance.ziti_edge` (`enable_openziti`) | Phase 2 OpenZiti edge host: controller, public router, IdP proxy |

```bash
terraform init
# lab_egress_cidr = the lab's public IP as /32 (curl -s https://checkip.amazonaws.com)
terraform plan  -var ssh_key_name=<key> -var lab_egress_cidr=<ip>/32
terraform apply -var ssh_key_name=<key> -var lab_egress_cidr=<ip>/32

# the data bucket name carries a random suffix; export it for the matrix
export LAB_DATA_BUCKET=$(terraform output -raw data_bucket)
```

Post-apply steps:

1. `aws iam create-access-key --user-name remote-<role>` for each role;
   configure as AWS profiles named after the roles on probing machines.
   Keys live only on those machines, never in the repo.
2. `export AWS_VPN_GATEWAY_IP=$(terraform output -raw vpn_gateway_public_ip)`
   and run ansible-openvpn: its first play configures this instance as
   the site-to-site hub, and tpi2-4 dials out to it (no inbound port on
   the lab side). Ingress to the gateway (1194/udp, 22/tcp) is limited
   to `lab_egress_cidr`; if the lab's public IP changes, re-apply with
   the new value.
3. Record `terraform version`, provider versions (`.terraform.lock.hcl`
   is committed), and the resolved AMI ID in the journal.

Phase 2 (OpenZiti, `phase2-openziti.tf`, docs/phase-2-openziti.md):

```bash
terraform apply -var ssh_key_name=<key> -var lab_egress_cidr=<ip>/32 -var enable_openziti=true
export LAB_EDGE_IP=$(terraform output -raw edge_host_public_ip)
```

The edge host gets its own subnet (10.100.1.0/24) and route table
(internet + on-prem via the hub), a security group open to the internet
on 80/443/1280/3022 (SSH from `lab_egress_cidr`), and an Elastic IP; the
hub's security group admits the edge subnet on the Keycloak port.
`enable_openziti=false` (default) leaves the Phase 1 environment unchanged.

Design notes:

- The workload security group deliberately admits all tunnel traffic:
  that over-breadth is the perimeter baseline under study. ZTNA phases
  add connector instances and tighten this group; keep those changes in
  separate, clearly named `.tf` files so the phase diff stays legible.
- The private subnet has no internet route (deliberate isolation), so
  `aws-app` is served by the AMI's python3 (`lab-app.service`) rather
  than a package installed at boot. Changing its user_data replaces the
  instance.
- Single region + fixed instance type per the performance-variability
  mitigation in the methodology.
- The data bucket is named `<data_bucket_name>-<6 random characters>`
  (default prefix `lab-data-bucket`) because S3 names are global. The
  suffix is stable across applies but new after every destroy/rebuild,
  so `test-matrix/matrix.yaml` reads it from `$LAB_DATA_BUCKET` rather
  than hardcoding it. Record the resolved name in the journal per run.
