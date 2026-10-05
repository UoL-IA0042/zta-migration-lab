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

```bash
terraform init
terraform plan  -var ssh_key_name=<key>
terraform apply -var ssh_key_name=<key>

# the data bucket name carries a random suffix; export it for the matrix
export LAB_DATA_BUCKET=$(terraform output -raw data_bucket)
```

Post-apply steps:

1. `aws iam create-access-key --user-name remote-<role>` for each role;
   configure as AWS profiles named after the roles on probing machines.
   Keys live only on those machines, never in the repo.
2. Point the ansible-openvpn site-to-site play at
   `vpn_gateway_public_ip`, then tighten the gateway security group's
   1194/udp ingress to the lab's egress IP.
3. Record `terraform version`, provider versions (`.terraform.lock.hcl`
   is committed), and the resolved AMI ID in the journal.

Design notes:

- The workload security group deliberately admits all tunnel traffic:
  that over-breadth is the perimeter baseline under study. ZTNA phases
  add connector instances and tighten this group; keep those changes in
  separate, clearly named `.tf` files so the phase diff stays legible.
- Single region + fixed instance type per the performance-variability
  mitigation in the methodology.
- The data bucket is named `<data_bucket_name>-<6 random characters>`
  (default prefix `lab-data-bucket`) because S3 names are global. The
  suffix is stable across applies but new after every destroy/rebuild,
  so `test-matrix/matrix.yaml` reads it from `$LAB_DATA_BUCKET` rather
  than hardcoding it. Record the resolved name in the journal per run.
