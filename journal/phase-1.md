## 2026-10-10 11:00-16:00 | phase-1 | ansible-openvpn | deployment
Created AWS access keys for the four test users
`remote-admin`
`remote-analyst`
`remote-developer`
`remote-contractor`

Updated `openvpn` version string in `requirements.yaml` to be correct and installed the `openvpn` module.

Having trouble with the lab network and the local gateway. It is owned by the service provider and has limited capabilities. I allows port-forwarding, but only to devices that it has handed out IP addresses to. Working to resolve the problem.

Resolved the problem by setting the MAC address to `00:52:83:67:c2:f5`. Now the node shows up in the app to allow port-forwarding for `openvpn`. Port-forwarding for `openvpn` on UDP port 1194 is now setup. I had to move the IP for the node to the gateway's DHCP range and update `inventory.yaml` to reflect the change. IPs for some of the other nodes will also need to be moved to that range for Phase 2.

Code changes were required for Phase 1 to continue. The changes are on branch `phase-1-network-fixes` and will be merged to main through a PR.

## 2026-10-10 16:00-17:45 | phase-1 | ansible-openvpn | deployment
```
$ terraform apply -var ssh_key_name=UoL-IA0042 -var lab_egress_cidr=$(curl -4 -s https://checkip.amazonaws.com)/32
random_string.bucket_suffix: Refreshing state... [id=m8k415]
data.aws_ami.ubuntu_arm64: Reading...
aws_iam_user.role_users["remote-analyst"]: Refreshing state... [id=remote-analyst]
aws_iam_user.role_users["remote-contractor"]: Refreshing state... [id=remote-contractor]
aws_iam_user.role_users["remote-admin"]: Refreshing state... [id=remote-admin]
aws_iam_user.role_users["remote-developer"]: Refreshing state... [id=remote-developer]
aws_vpc.lab: Refreshing state... [id=vpc-0e323ba9258e65156]
aws_s3_bucket.data: Refreshing state... [id=lab-data-bucket-m8k415]
data.aws_ami.ubuntu_arm64: Read complete after 0s [id=ami-0ac0ed4cc59d81934]
aws_internet_gateway.igw: Refreshing state... [id=igw-06f896d5cffcb011e]
aws_subnet.public: Refreshing state... [id=subnet-01cf32af4e477ea6b]
aws_security_group.workload: Refreshing state... [id=sg-0fc7bc85ea7ef3fc3]
aws_subnet.private: Refreshing state... [id=subnet-04c7c617caf0628c9]
aws_security_group.vpn_gateway: Refreshing state... [id=sg-0d61d59f641036bea]
aws_route_table.public: Refreshing state... [id=rtb-0441dc354c986e027]
aws_s3_bucket_public_access_block.data: Refreshing state... [id=lab-data-bucket-m8k415]
data.aws_iam_policy_document.s3_write: Reading...
aws_s3_object.probe_seed: Refreshing state... [id=lab-data-bucket-m8k415/probe.txt]
data.aws_iam_policy_document.s3_read: Reading...
data.aws_iam_policy_document.s3_write: Read complete after 0s [id=3512013586]
data.aws_iam_policy_document.s3_read: Read complete after 0s [id=3946160476]
aws_iam_policy.s3_write: Refreshing state... [id=arn:aws:iam::<account-id>:policy/zta-lab-s3-write]
aws_iam_policy.s3_read: Refreshing state... [id=arn:aws:iam::<account-id>:policy/zta-lab-s3-read]
aws_instance.vpn_gateway: Refreshing state... [id=i-08e5aaf4219a04872]
aws_instance.app: Refreshing state... [id=i-0d30a5d0816aa57bc]
aws_route_table_association.public: Refreshing state... [id=rtbassoc-0ab9ce32e86af2f14]
aws_iam_user_policy_attachment.read["remote-analyst"]: Refreshing state... [id=remote-analyst/arn:aws:iam::<account-id>:policy/zta-lab-s3-read]
aws_iam_user_policy_attachment.read["remote-admin"]: Refreshing state... [id=remote-admin/arn:aws:iam::<account-id>:policy/zta-lab-s3-read]
aws_iam_user_policy_attachment.read["remote-developer"]: Refreshing state... [id=remote-developer/arn:aws:iam::<account-id>:policy/zta-lab-s3-read]
aws_iam_user_policy_attachment.write["remote-admin"]: Refreshing state... [id=remote-admin/arn:aws:iam::<account-id>:policy/zta-lab-s3-write]
aws_route_table.private: Refreshing state... [id=rtb-05a9d2c188ba97454]
aws_route_table_association.private: Refreshing state... [id=rtbassoc-08f4025d50d79088c]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create
  ~ update in-place
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # aws_eip.vpn_gateway will be created
  + resource "aws_eip" "vpn_gateway" {
      + allocation_id        = (known after apply)
      + arn                  = (known after apply)
      + association_id       = (known after apply)
      + carrier_ip           = (known after apply)
      + customer_owned_ip    = (known after apply)
      + domain               = "vpc"
      + id                   = (known after apply)
      + instance             = (known after apply)
      + ipam_pool_id         = (known after apply)
      + network_border_group = (known after apply)
      + network_interface    = (known after apply)
      + private_dns          = (known after apply)
      + private_ip           = (known after apply)
      + ptr_record           = (known after apply)
      + public_dns           = (known after apply)
      + public_ip            = (known after apply)
      + public_ipv4_pool     = (known after apply)
      + region               = "us-west-2"
      + tags                 = {
          + "Name" = "zta-lab-vpn-gateway"
        }
      + tags_all             = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab-vpn-gateway"
          + "Project" = "zta-migration-lab"
        }
    }

  # aws_instance.app must be replaced
-/+ resource "aws_instance" "app" {
      ~ ami                                  = "ami-06c11807f6c511068" -> "ami-0ac0ed4cc59d81934" # forces replacement
      ~ arn                                  = "arn:aws:ec2:us-west-2:<account-id>:instance/i-0d30a5d0816aa57bc" -> (known after apply)
      ~ associate_public_ip_address          = false -> (known after apply)
      ~ availability_zone                    = "us-west-2c" -> (known after apply)
      ~ disable_api_stop                     = false -> (known after apply)
      ~ disable_api_termination              = false -> (known after apply)
      ~ ebs_optimized                        = false -> (known after apply)
      + enable_primary_ipv6                  = (known after apply)
      - hibernation                          = false -> null
      + host_id                              = (known after apply)
      + host_resource_group_arn              = (known after apply)
      + iam_instance_profile                 = (known after apply)
      ~ id                                   = "i-0d30a5d0816aa57bc" -> (known after apply)
      ~ instance_initiated_shutdown_behavior = "stop" -> (known after apply)
      + instance_lifecycle                   = (known after apply)
      ~ instance_state                       = "running" -> (known after apply)
      ~ ipv6_address_count                   = 0 -> (known after apply)
      ~ ipv6_addresses                       = [] -> (known after apply)
      ~ monitoring                           = false -> (known after apply)
      + outpost_arn                          = (known after apply)
      + password_data                        = (known after apply)
      + placement_group                      = (known after apply)
      + placement_group_id                   = (known after apply)
      ~ placement_partition_number           = 0 -> (known after apply)
      ~ primary_network_interface_id         = "eni-0f9ab73f4ad11a211" -> (known after apply)
      ~ private_dns                          = "ip-10-100-10-10.us-west-2.compute.internal" -> (known after apply)
      + public_dns                           = (known after apply)
      + public_ip                            = (known after apply)
      ~ secondary_private_ips                = [] -> (known after apply)
      ~ security_groups                      = [] -> (known after apply)
      + spot_instance_request_id             = (known after apply)
        tags                                 = {
            "Name" = "zta-lab-app"
        }
      ~ tenancy                              = "default" -> (known after apply)
      ~ user_data                            = <<-EOT # forces replacement
            #!/bin/bash
          - apt-get update && apt-get install -y nginx
          - sed -i 's/listen 80/listen 8080/' /etc/nginx/sites-available/default
          - echo '<h1>AWS lab application</h1>' > /var/www/html/index.html
          - systemctl restart nginx
          + set -euo pipefail
          + mkdir -p /srv/lab-app
          + echo '<h1>AWS lab application</h1>' > /srv/lab-app/index.html
          + cat > /etc/systemd/system/lab-app.service <<'UNIT'
          + [Unit]
          + Description=AWS lab application (matrix: aws-app)
          + After=network-online.target
          + Wants=network-online.target
          + [Service]
          + ExecStart=/usr/bin/python3 -m http.server 8080 --directory /srv/lab-app
          + DynamicUser=yes
          + Restart=always
          + [Install]
          + WantedBy=multi-user.target
          + UNIT
          + systemctl daemon-reload
          + systemctl enable --now lab-app.service
        EOT
      + user_data_base64                     = (known after apply)
      ~ user_data_replace_on_change          = false -> true
        # (10 unchanged attributes hidden)

      ~ capacity_reservation_specification (known after apply)
      - capacity_reservation_specification {
          - capacity_reservation_preference = "open" -> null
        }

      ~ cpu_options (known after apply)
      - cpu_options {
          - core_count            = 2 -> null
          - threads_per_core      = 1 -> null
            # (2 unchanged attributes hidden)
        }

      - credit_specification {
          - cpu_credits = "unlimited" -> null
        }

      ~ ebs_block_device (known after apply)

      ~ enclave_options (known after apply)
      - enclave_options {
          - enabled = false -> null
        }

      ~ ephemeral_block_device (known after apply)

      ~ instance_market_options (known after apply)

      ~ maintenance_options (known after apply)
      - maintenance_options {
          - auto_recovery = "default" -> null
        }

      ~ metadata_options (known after apply)
      - metadata_options {
          - http_endpoint               = "enabled" -> null
          - http_protocol_ipv6          = "disabled" -> null
          - http_put_response_hop_limit = 2 -> null
          - http_tokens                 = "required" -> null
          - instance_metadata_tags      = "disabled" -> null
        }

      ~ network_interface (known after apply)

      ~ primary_network_interface (known after apply)
      - primary_network_interface {
          - delete_on_termination = true -> null
          - network_interface_id  = "eni-0f9ab73f4ad11a211" -> null
        }

      ~ private_dns_name_options (known after apply)
      - private_dns_name_options {
          - enable_resource_name_dns_a_record    = false -> null
          - enable_resource_name_dns_aaaa_record = false -> null
          - hostname_type                        = "ip-name" -> null
        }

      ~ root_block_device (known after apply)
      - root_block_device {
          - delete_on_termination = true -> null
          - device_name           = "/dev/sda1" -> null
          - encrypted             = false -> null
          - iops                  = 3000 -> null
          - tags                  = {
              - "Managed" = "terraform"
              - "Project" = "zta-migration-lab"
            } -> null
          - tags_all              = {
              - "Managed" = "terraform"
              - "Project" = "zta-migration-lab"
            } -> null
          - throughput            = 125 -> null
          - volume_id             = "vol-0e3c54c368cabfd01" -> null
          - volume_size           = 8 -> null
          - volume_type           = "gp3" -> null
            # (1 unchanged attribute hidden)
        }

      ~ secondary_network_interface (known after apply)
    }

  # aws_instance.vpn_gateway must be replaced
-/+ resource "aws_instance" "vpn_gateway" {
      ~ ami                                  = "ami-06c11807f6c511068" -> "ami-0ac0ed4cc59d81934" # forces replacement
      ~ arn                                  = "arn:aws:ec2:us-west-2:<account-id>:instance/i-08e5aaf4219a04872" -> (known after apply)
      ~ associate_public_ip_address          = true -> (known after apply)
      ~ availability_zone                    = "us-west-2b" -> (known after apply)
      ~ disable_api_stop                     = false -> (known after apply)
      ~ disable_api_termination              = false -> (known after apply)
      ~ ebs_optimized                        = false -> (known after apply)
      + enable_primary_ipv6                  = (known after apply)
      - hibernation                          = false -> null
      + host_id                              = (known after apply)
      + host_resource_group_arn              = (known after apply)
      + iam_instance_profile                 = (known after apply)
      ~ id                                   = "i-08e5aaf4219a04872" -> (known after apply)
      ~ instance_initiated_shutdown_behavior = "stop" -> (known after apply)
      + instance_lifecycle                   = (known after apply)
      ~ instance_state                       = "running" -> (known after apply)
      ~ ipv6_address_count                   = 0 -> (known after apply)
      ~ ipv6_addresses                       = [] -> (known after apply)
      ~ monitoring                           = false -> (known after apply)
      + outpost_arn                          = (known after apply)
      + password_data                        = (known after apply)
      + placement_group                      = (known after apply)
      + placement_group_id                   = (known after apply)
      ~ placement_partition_number           = 0 -> (known after apply)
      ~ primary_network_interface_id         = "eni-01cb2c440da63000f" -> (known after apply)
      ~ private_dns                          = "ip-10-100-0-59.us-west-2.compute.internal" -> (known after apply)
      ~ private_ip                           = "10.100.0.59" -> (known after apply)
      ~ public_dns                           = "ec2-<hub-eip-dashed>.us-west-2.compute.amazonaws.com" -> (known after apply)
      ~ public_ip                            = "<hub-eip>" -> (known after apply)
      ~ secondary_private_ips                = [] -> (known after apply)
      ~ security_groups                      = [] -> (known after apply)
      + spot_instance_request_id             = (known after apply)
        tags                                 = {
            "Name" = "zta-lab-vpn-gateway"
        }
      ~ tenancy                              = "default" -> (known after apply)
      + user_data_base64                     = (known after apply)
        # (10 unchanged attributes hidden)

      ~ capacity_reservation_specification (known after apply)
      - capacity_reservation_specification {
          - capacity_reservation_preference = "open" -> null
        }

      ~ cpu_options (known after apply)
      - cpu_options {
          - core_count            = 2 -> null
          - threads_per_core      = 1 -> null
            # (2 unchanged attributes hidden)
        }

      - credit_specification {
          - cpu_credits = "unlimited" -> null
        }

      ~ ebs_block_device (known after apply)

      ~ enclave_options (known after apply)
      - enclave_options {
          - enabled = false -> null
        }

      ~ ephemeral_block_device (known after apply)

      ~ instance_market_options (known after apply)

      ~ maintenance_options (known after apply)
      - maintenance_options {
          - auto_recovery = "default" -> null
        }

      ~ metadata_options (known after apply)
      - metadata_options {
          - http_endpoint               = "enabled" -> null
          - http_protocol_ipv6          = "disabled" -> null
          - http_put_response_hop_limit = 2 -> null
          - http_tokens                 = "required" -> null
          - instance_metadata_tags      = "disabled" -> null
        }

      ~ network_interface (known after apply)

      ~ primary_network_interface (known after apply)
      - primary_network_interface {
          - delete_on_termination = true -> null
          - network_interface_id  = "eni-01cb2c440da63000f" -> null
        }

      ~ private_dns_name_options (known after apply)
      - private_dns_name_options {
          - enable_resource_name_dns_a_record    = false -> null
          - enable_resource_name_dns_aaaa_record = false -> null
          - hostname_type                        = "ip-name" -> null
        }

      ~ root_block_device (known after apply)
      - root_block_device {
          - delete_on_termination = true -> null
          - device_name           = "/dev/sda1" -> null
          - encrypted             = false -> null
          - iops                  = 3000 -> null
          - tags                  = {
              - "Managed" = "terraform"
              - "Project" = "zta-migration-lab"
            } -> null
          - tags_all              = {
              - "Managed" = "terraform"
              - "Project" = "zta-migration-lab"
            } -> null
          - throughput            = 125 -> null
          - volume_id             = "vol-06fbeaf57506391e3" -> null
          - volume_size           = 8 -> null
          - volume_type           = "gp3" -> null
            # (1 unchanged attribute hidden)
        }

      ~ secondary_network_interface (known after apply)
    }

  # aws_route_table.private will be updated in-place
  ~ resource "aws_route_table" "private" {
        id               = "rtb-05a9d2c188ba97454"
      ~ route            = [
          - {
              - cidr_block                 = "10.0.0.0/24"
              - network_interface_id       = "eni-01cb2c440da63000f"
                # (12 unchanged attributes hidden)
            },
          - {
              - cidr_block                 = "10.9.0.0/24"
              - network_interface_id       = "eni-01cb2c440da63000f"
                # (12 unchanged attributes hidden)
            },
          + {
              + cidr_block                 = "10.0.0.0/24"
              + network_interface_id       = (known after apply)
                # (12 unchanged attributes hidden)
            },
          + {
              + cidr_block                 = "10.9.0.0/24"
              + network_interface_id       = (known after apply)
                # (12 unchanged attributes hidden)
            },
        ]
        tags             = {}
        # (6 unchanged attributes hidden)
    }

  # aws_security_group.vpn_gateway will be updated in-place
  ~ resource "aws_security_group" "vpn_gateway" {
        id                     = "sg-0d61d59f641036bea"
      ~ ingress                = [
          - {
              - cidr_blocks      = [
                  - "0.0.0.0/0",
                ]
              - description      = "OpenVPN site-to-site from the public address of the lab"
              - from_port        = 1194
              - ipv6_cidr_blocks = []
              - prefix_list_ids  = []
              - protocol         = "udp"
              - security_groups  = []
              - self             = false
              - to_port          = 1194
            },
          + {
              + cidr_blocks      = [
                  + "<lab-egress-ip>/32",
                ]
              + description      = "OpenVPN site-to-site from the public address of the lab"
              + from_port        = 1194
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "udp"
              + security_groups  = []
              + self             = false
              + to_port          = 1194
            },
          + {
              + cidr_blocks      = [
                  + "<lab-egress-ip>/32",
                ]
              + description      = "SSH from the lab (ansible-openvpn configures this host)"
              + from_port        = 22
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "tcp"
              + security_groups  = []
              + self             = false
              + to_port          = 22
            },
        ]
        name                   = "zta-lab-vpn-gateway"
        tags                   = {}
        # (9 unchanged attributes hidden)
    }

Plan: 3 to add, 2 to change, 2 to destroy.

Changes to Outputs:
  ~ vpn_gateway_public_ip = "<hub-eip>" -> (known after apply)

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

aws_instance.vpn_gateway: Destroying... [id=i-08e5aaf4219a04872]
aws_instance.app: Destroying... [id=i-0d30a5d0816aa57bc]
aws_instance.vpn_gateway: Still destroying... [id=i-08e5aaf4219a04872, 00m10s elapsed]
aws_instance.app: Still destroying... [id=i-0d30a5d0816aa57bc, 00m10s elapsed]
aws_instance.vpn_gateway: Destruction complete after 20s
aws_security_group.vpn_gateway: Modifying... [id=sg-0d61d59f641036bea]
aws_instance.app: Still destroying... [id=i-0d30a5d0816aa57bc, 00m20s elapsed]
aws_security_group.vpn_gateway: Modifications complete after 1s [id=sg-0d61d59f641036bea]
aws_instance.vpn_gateway: Creating...
aws_instance.app: Still destroying... [id=i-0d30a5d0816aa57bc, 00m30s elapsed]
aws_instance.app: Destruction complete after 30s
aws_instance.app: Creating...
aws_instance.vpn_gateway: Still creating... [00m10s elapsed]
aws_instance.vpn_gateway: Creation complete after 13s [id=i-0c09395211c98e379]
aws_eip.vpn_gateway: Creating...
aws_route_table.private: Modifying... [id=rtb-05a9d2c188ba97454]
aws_route_table.private: Modifications complete after 1s [id=rtb-05a9d2c188ba97454]
aws_eip.vpn_gateway: Creation complete after 2s [id=eipalloc-0b2b95b8d05c73e1d]
aws_instance.app: Still creating... [00m10s elapsed]
aws_instance.app: Creation complete after 13s [id=i-0fe0d03ac5b9f31e0]

Apply complete! Resources: 3 added, 2 changed, 2 destroyed.
```

There were some ssh and DNS issues that needed to be sorted out to proceed with Phase 1. They were committed to a branch (`phase-1-dns-and-reset-fixes`), merged into `main`.

```
$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-4 --tags to-recovery

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-4]

TASK [Mount recovery partition (from main OS)] *****************************************************************************************************************************
changed: [tpi2-4]

TASK [Check recovery extlinux state] ***************************************************************************************************************************************
ok: [tpi2-4]

TASK [Assert recovery extlinux exists (enabled or disabled)] ***************************************************************************************************************
ok: [tpi2-4]

TASK [Enable recovery boot (rename extlinux.conf into place)] **************************************************************************************************************
changed: [tpi2-4]

TASK [Unmount recovery partition] ******************************************************************************************************************************************
changed: [tpi2-4]

TASK [Reboot into recovery OS (NVMe wins the boot scan)] *******************************************************************************************************************
changed: [tpi2-4]

TASK [Confirm recovery OS (root on NVMe, eMMC root unmounted)] *************************************************************************************************************
ok: [tpi2-4]

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-4                     : ok=8    changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## 2026-10-10 17:50-20:45 | phase-1 | ansible-openvpn | deployment
Testing the recovery process to ensure it works as expected.

```
$ ssh tpi2-4 'cat /etc/recovery-os; findmnt -n -o SOURCE /; findmnt -n -o SOURCE /data'
tpi2-4 recovery OS, cloned 2026-10-11T00:25:54Z
/dev/nvme0n1p1
/dev/nvme0n1p2
$ ./capture-golden.sh tpi2-4 10.0.0.251
capturing /dev/mmcblk0p2 on 10.0.0.251 -> /data/golden/rootfs.img.zst
31239176192 bytes (31 GB, 29 GiB) copied, 126 s, 248 MB/s
7449+1 records in
7449+1 records out
31247547904 bytes (31 GB, 29 GiB) copied, 129.456 s, 241 MB/s
/*stdin*\            :  7.33%   (  29.1 GiB =>   2.13 GiB, /data/golden/rootfs.img.zst.new) 
total 2.2G
-rw-r--r-- 1 root root 2.2G Oct 11 00:45 rootfs.img.zst
-rw-r--r-- 1 root root   98 Oct 11 00:45 rootfs.sha256
captured. Record image identity in the journal:
99d7f29953b69f4c37198fb260c7f23cd0c42fbf4f7ef8abd4da434f4276f872  /data/golden/rootfs.img.zst.new
```

Full run of the `reset` playbook as final verification.

```
$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-4

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-4]

TASK [Mount recovery partition (from main OS)] *****************************************************************************************************************************
changed: [tpi2-4]

TASK [Check recovery extlinux state] ***************************************************************************************************************************************
ok: [tpi2-4]

TASK [Assert recovery extlinux exists (enabled or disabled)] ***************************************************************************************************************
ok: [tpi2-4]

TASK [Enable recovery boot (rename extlinux.conf into place)] **************************************************************************************************************
skipping: [tpi2-4]

TASK [Unmount recovery partition] ******************************************************************************************************************************************
changed: [tpi2-4]

TASK [Reboot into recovery OS (NVMe wins the boot scan)] *******************************************************************************************************************
changed: [tpi2-4]

TASK [Confirm recovery OS (root on NVMe, eMMC root unmounted)] *************************************************************************************************************
ok: [tpi2-4]

TASK [Verify golden image checksum] ****************************************************************************************************************************************
[ERROR]: Task failed: Module failed: The command exited with a non-zero return code.
Origin: /Users/<user>/dev/CYM500/zta-migration-lab/node-reset/reset.yaml:75:7

73
74     # --------------------------------------------------------- restore
75     - name: Verify golden image checksum
         ^ column 7

fatal: [tpi2-4]: FAILED! => {"changed": false, "changed_when_result": false, "cmd": "cd /data/golden && sha256sum -c rootfs.sha256\n", "delta": "0:00:00.014091", "end": "2026-10-11 00:48:33.809658", "msg": "The command exited with a non-zero return code.", "rc": 1, "start": "2026-10-11 00:48:33.795567", "stderr": "sha256sum: /data/golden/rootfs.img.zst.new: No such file or directory\nsha256sum: WARNING: 1 listed file could not be read", "stderr_lines": ["sha256sum: /data/golden/rootfs.img.zst.new: No such file or directory", "sha256sum: WARNING: 1 listed file could not be read"], "stdout": "/data/golden/rootfs.img.zst.new: FAILED open or read", "stdout_lines": ["/data/golden/rootfs.img.zst.new: FAILED open or read"]}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-4                     : ok=7    changed=3    unreachable=0    failed=1    skipped=1    rescued=0    ignored=0
```

Run manually on the node

```
ubuntu@tpi2-4:~$ cd /data/golden
ubuntu@tpi2-4:/data/golden$ cat rootfs.sha256
99d7f29953b69f4c37198fb260c7f23cd0c42fbf4f7ef8abd4da434f4276f872  /data/golden/rootfs.img.zst.new
ubuntu@tpi2-4:/data/golden$ sudo sed -i 's|[^ ]*rootfs\.img\.zst\.new$|rootfs.img.zst|' rootfs.sha256
ubuntu@tpi2-4:/data/golden$ cat rootfs.sha256
99d7f29953b69f4c37198fb260c7f23cd0c42fbf4f7ef8abd4da434f4276f872  rootfs.img.zst
ubuntu@tpi2-4:/data/golden$ sha256sum -c rootfs.sha256
rootfs.img.zst: OK
```

Two defects turned up in the first full reset, and both failed safely before anything was written. The checksum file named the temporary .new file, and the restore used pipefail under dash.

```
$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-4 --tags restore,to-main,verify

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-4]

TASK [Verify golden image checksum] ****************************************************************************************************************************************
ok: [tpi2-4]

TASK [Restore golden image onto eMMC root partition] ***********************************************************************************************************************
changed: [tpi2-4]

TASK [Run filesystem check on restored root] *******************************************************************************************************************************
ok: [tpi2-4]

TASK [Mount restored root and confirm it is bootable] **********************************************************************************************************************
changed: [tpi2-4]

TASK [Confirm restored extlinux.conf present on main root] *****************************************************************************************************************
ok: [tpi2-4]

TASK [Unmount restored root] ***********************************************************************************************************************************************
changed: [tpi2-4]

TASK [Disable recovery boot (recovery renames its own extlinux)] ***********************************************************************************************************
changed: [tpi2-4]

TASK [Reboot into restored main OS (scan falls through to eMMC)] ***********************************************************************************************************
changed: [tpi2-4]

TASK [Verify main OS booted from eMMC] *************************************************************************************************************************************
ok: [tpi2-4]

TASK [Read golden image provenance marker] *********************************************************************************************************************************
ok: [tpi2-4]

TASK [Report reset provenance (journal this)] ******************************************************************************************************************************
ok: [tpi2-4] => {
    "msg": "tpi2-4 restored to golden: tpi2-4 2026-10-11T00:23:24Z phase-0 baseline"
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-4                     : ok=12   changed=5    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

There was a new `node-reset` playbook added (`setup-recovery.yaml`), and it is run on the remaining nodes to ensure recovery is streamlined. It was developed on a branch (`node-reset-setup-playbook`) and merged into `main`.

Output from the runs on each node.
`tpi2-1`
```
$ ansible-playbook -i inventory.yaml setup-recovery.yaml -l tpi2-1 -e confirm_wipe_nvme=yes

PLAY [Set up recovery OS and data partition] *******************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-1]

TASK [Require explicit confirmation (erases the NVMe)] *********************************************************************************************************************
ok: [tpi2-1]

TASK [Read NVMe partition layout] ******************************************************************************************************************************************
ok: [tpi2-1]

TASK [Classify the layout] *************************************************************************************************************************************************
ok: [tpi2-1]

TASK [Classify the layout (already set up?)] *******************************************************************************************************************************
ok: [tpi2-1]

TASK [Already set up, nothing to do] ***************************************************************************************************************************************
skipping: [tpi2-1]

TASK [Skip a node that is already set up] **********************************************************************************************************************************
skipping: [tpi2-1]

TASK [Require the factory layout (one whole-disk partition on /data)] ******************************************************************************************************
ok: [tpi2-1] => {
    "changed": false,
    "msg": "All assertions passed"
}

TASK [Require the main OS (root on the eMMC)] ******************************************************************************************************************************
ok: [tpi2-1]

TASK [Install tools (partitioning, clone, capture)] ************************************************************************************************************************
ok: [tpi2-1]

TASK [Measure data on /data (excluding lost+found)] ************************************************************************************************************************
ok: [tpi2-1]

TASK [Refuse to erase a non-empty /data] ***********************************************************************************************************************************
ok: [tpi2-1]

TASK [Refuse if a process is using /data] **********************************************************************************************************************************
ok: [tpi2-1]

TASK [Unmount any stray recovery mount] ************************************************************************************************************************************
ok: [tpi2-1]

TASK [Unmount /data and drop its old fstab entry] **************************************************************************************************************************
changed: [tpi2-1]

TASK [Wipe and repartition the NVMe] ***************************************************************************************************************************************
changed: [tpi2-1]

TASK [Create filesystems] **************************************************************************************************************************************************
changed: [tpi2-1] => (item={'dev': '/dev/nvme0n1p1', 'label': 'recovery'})
changed: [tpi2-1] => (item={'dev': '/dev/nvme0n1p2', 'label': 'data'})

TASK [Read filesystem UUIDs] ***********************************************************************************************************************************************
ok: [tpi2-1] => (item=/dev/nvme0n1p1)
ok: [tpi2-1] => (item=/dev/nvme0n1p2)
ok: [tpi2-1] => (item=/dev/mmcblk0p2)

TASK [Record UUIDs] ********************************************************************************************************************************************************
ok: [tpi2-1]

TASK [Mount the new /data by UUID (nofail)] ********************************************************************************************************************************
changed: [tpi2-1]

TASK [Write the golden-image provenance marker on main (if absent)] ********************************************************************************************************
changed: [tpi2-1]

TASK [Mount the recovery partition (ephemeral)] ****************************************************************************************************************************
changed: [tpi2-1]

TASK [Clone the main root into the recovery partition] *********************************************************************************************************************
changed: [tpi2-1]

TASK [Point the recovery root and boot entry at the recovery partition] ****************************************************************************************************
changed: [tpi2-1] => (item=/etc/fstab)
changed: [tpi2-1] => (item=/boot/extlinux/extlinux.conf)

TASK [Check for u-boot-update defaults in the recovery OS] *****************************************************************************************************************
ok: [tpi2-1]

TASK [Point u-boot-update at the recovery partition] ***********************************************************************************************************************
ok: [tpi2-1]

TASK [Label the recovery boot entries] *************************************************************************************************************************************
changed: [tpi2-1]

TASK [Disable cloud-init in the recovery OS] *******************************************************************************************************************************
changed: [tpi2-1]

TASK [Mark the recovery OS] ************************************************************************************************************************************************
changed: [tpi2-1]

TASK [Remove the golden marker from the recovery OS (it belongs to main)] **************************************************************************************************
changed: [tpi2-1]

TASK [Disable lab services in the recovery OS] *****************************************************************************************************************************
changed: [tpi2-1] => (item=docker.socket)
changed: [tpi2-1] => (item=docker.service)
changed: [tpi2-1] => (item=containerd.service)
changed: [tpi2-1] => (item=alloy.service)
ok: [tpi2-1] => (item=k3s.service)
ok: [tpi2-1] => (item=k3s-agent.service)
ok: [tpi2-1] => (item=unattended-upgrades.service)
changed: [tpi2-1] => (item=apt-daily.timer)
changed: [tpi2-1] => (item=apt-daily-upgrade.timer)

TASK [Leave the boot switch DISABLED] **************************************************************************************************************************************
changed: [tpi2-1]

TASK [Verify the recovery tree] ********************************************************************************************************************************************
ok: [tpi2-1]

TASK [Unmount the recovery partition] **************************************************************************************************************************************
changed: [tpi2-1]

TASK [Report (journal this)] ***********************************************************************************************************************************************
ok: [tpi2-1] => {
    "msg": "tpi2-1: recovery=fa4093c5-0fae-4f3b-92ce-9fd3d268b4d3 data=60091675-8f39-4cb2-a0a2-74a0a802b921 main=ad692498-9c48-4e70-a1b1-368301614a6f; boot switch disabled. Next: reset.yaml --tags to-recovery."
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-1                     : ok=33   changed=15   unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-1 --tags to-recovery

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-1]

TASK [Mount recovery partition (from main OS)] *****************************************************************************************************************************
changed: [tpi2-1]

TASK [Check recovery extlinux state] ***************************************************************************************************************************************
ok: [tpi2-1]

TASK [Assert recovery extlinux exists (enabled or disabled)] ***************************************************************************************************************
ok: [tpi2-1]

TASK [Enable recovery boot (rename extlinux.conf into place)] **************************************************************************************************************
changed: [tpi2-1]

TASK [Unmount recovery partition] ******************************************************************************************************************************************
changed: [tpi2-1]

TASK [Reboot into recovery OS (NVMe wins the boot scan)] *******************************************************************************************************************
changed: [tpi2-1]

TASK [Confirm recovery OS (root on NVMe, eMMC root unmounted)] *************************************************************************************************************
ok: [tpi2-1]

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-1                     : ok=8    changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

$ ./capture-golden.sh tpi2-1 10.0.0.71
capturing /dev/mmcblk0p2 on 10.0.0.71 -> /data/golden/rootfs.img.zst
31088181248 bytes (31 GB, 29 GiB) copied, 128 s, 243 MB/s
7449+1 records in
7449+1 records out
31247547904 bytes (31 GB, 29 GiB) copied, 132.081 s, 237 MB/s
/*stdin*\            : 10.55%   (  29.1 GiB =>   3.07 GiB, /data/golden/rootfs.img.zst.new) 
rootfs.img.zst: OK
total 3.1G
-rw-r--r-- 1 root root 3.1G Oct 11 02:01 rootfs.img.zst
-rw-r--r-- 1 root root   81 Oct 11 02:01 rootfs.sha256
captured. Record image identity in the journal:
5b4daad9347645de04145fae9ed1286a708839a39d27b095e463e996b8587387  rootfs.img.zst
$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-1 --tags to-main,verify

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-1]

TASK [Disable recovery boot (recovery renames its own extlinux)] ***********************************************************************************************************
changed: [tpi2-1]

TASK [Reboot into restored main OS (scan falls through to eMMC)] ***********************************************************************************************************
changed: [tpi2-1]

TASK [Verify main OS booted from eMMC] *************************************************************************************************************************************
ok: [tpi2-1]

TASK [Read golden image provenance marker] *********************************************************************************************************************************
ok: [tpi2-1]

TASK [Report reset provenance (journal this)] ******************************************************************************************************************************
ok: [tpi2-1] => {
    "msg": "tpi2-1 restored to golden: tpi2-1 2026-10-11T01:26:04Z phase-0 baseline"
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-1                     : ok=6    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-1

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-1]

TASK [Mount recovery partition (from main OS)] *****************************************************************************************************************************
changed: [tpi2-1]

TASK [Check recovery extlinux state] ***************************************************************************************************************************************
ok: [tpi2-1]

TASK [Assert recovery extlinux exists (enabled or disabled)] ***************************************************************************************************************
ok: [tpi2-1]

TASK [Enable recovery boot (rename extlinux.conf into place)] **************************************************************************************************************
changed: [tpi2-1]

TASK [Unmount recovery partition] ******************************************************************************************************************************************
changed: [tpi2-1]

TASK [Reboot into recovery OS (NVMe wins the boot scan)] *******************************************************************************************************************
changed: [tpi2-1]

TASK [Confirm recovery OS (root on NVMe, eMMC root unmounted)] *************************************************************************************************************
ok: [tpi2-1]

TASK [Verify golden image checksum] ****************************************************************************************************************************************
ok: [tpi2-1]

TASK [Restore golden image onto eMMC root partition] ***********************************************************************************************************************
changed: [tpi2-1]

TASK [Run filesystem check on restored root] *******************************************************************************************************************************
ok: [tpi2-1]

TASK [Mount restored root and confirm it is bootable] **********************************************************************************************************************
changed: [tpi2-1]

TASK [Confirm restored extlinux.conf present on main root] *****************************************************************************************************************
ok: [tpi2-1]

TASK [Unmount restored root] ***********************************************************************************************************************************************
changed: [tpi2-1]

TASK [Disable recovery boot (recovery renames its own extlinux)] ***********************************************************************************************************
changed: [tpi2-1]

TASK [Reboot into restored main OS (scan falls through to eMMC)] ***********************************************************************************************************
changed: [tpi2-1]

TASK [Verify main OS booted from eMMC] *************************************************************************************************************************************
ok: [tpi2-1]

TASK [Read golden image provenance marker] *********************************************************************************************************************************
ok: [tpi2-1]

TASK [Report reset provenance (journal this)] ******************************************************************************************************************************
ok: [tpi2-1] => {
    "msg": "tpi2-1 restored to golden: tpi2-1 2026-10-11T01:26:04Z phase-0 baseline"
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-1                     : ok=19   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

`tpi2-2`
```
$ ansible-playbook -i inventory.yaml setup-recovery.yaml -l tpi2-2 -e confirm_wipe_nvme=yes

PLAY [Set up recovery OS and data partition] *******************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-2]

TASK [Require explicit confirmation (erases the NVMe)] *********************************************************************************************************************
ok: [tpi2-2]

TASK [Read NVMe partition layout] ******************************************************************************************************************************************
ok: [tpi2-2]

TASK [Classify the layout] *************************************************************************************************************************************************
ok: [tpi2-2]

TASK [Classify the layout (already set up?)] *******************************************************************************************************************************
ok: [tpi2-2]

TASK [Already set up, nothing to do] ***************************************************************************************************************************************
skipping: [tpi2-2]

TASK [Skip a node that is already set up] **********************************************************************************************************************************
skipping: [tpi2-2]

TASK [Require the factory layout (one whole-disk partition on /data)] ******************************************************************************************************
ok: [tpi2-2] => {
    "changed": false,
    "msg": "All assertions passed"
}

TASK [Require the main OS (root on the eMMC)] ******************************************************************************************************************************
ok: [tpi2-2]

TASK [Install tools (partitioning, clone, capture)] ************************************************************************************************************************
ok: [tpi2-2]

TASK [Measure data on /data (excluding lost+found)] ************************************************************************************************************************
ok: [tpi2-2]

TASK [Refuse to erase a non-empty /data] ***********************************************************************************************************************************
ok: [tpi2-2]

TASK [Refuse if a process is using /data] **********************************************************************************************************************************
ok: [tpi2-2]

TASK [Unmount any stray recovery mount] ************************************************************************************************************************************
ok: [tpi2-2]

TASK [Unmount /data and drop its old fstab entry] **************************************************************************************************************************
changed: [tpi2-2]

TASK [Wipe and repartition the NVMe] ***************************************************************************************************************************************
changed: [tpi2-2]

TASK [Create filesystems] **************************************************************************************************************************************************
changed: [tpi2-2] => (item={'dev': '/dev/nvme0n1p1', 'label': 'recovery'})
changed: [tpi2-2] => (item={'dev': '/dev/nvme0n1p2', 'label': 'data'})

TASK [Read filesystem UUIDs] ***********************************************************************************************************************************************
ok: [tpi2-2] => (item=/dev/nvme0n1p1)
ok: [tpi2-2] => (item=/dev/nvme0n1p2)
ok: [tpi2-2] => (item=/dev/mmcblk0p2)

TASK [Record UUIDs] ********************************************************************************************************************************************************
ok: [tpi2-2]

TASK [Mount the new /data by UUID (nofail)] ********************************************************************************************************************************
changed: [tpi2-2]

TASK [Write the golden-image provenance marker on main (if absent)] ********************************************************************************************************
changed: [tpi2-2]

TASK [Mount the recovery partition (ephemeral)] ****************************************************************************************************************************
changed: [tpi2-2]

TASK [Clone the main root into the recovery partition] *********************************************************************************************************************
changed: [tpi2-2]

TASK [Point the recovery root and boot entry at the recovery partition] ****************************************************************************************************
changed: [tpi2-2] => (item=/etc/fstab)
changed: [tpi2-2] => (item=/boot/extlinux/extlinux.conf)

TASK [Check for u-boot-update defaults in the recovery OS] *****************************************************************************************************************
ok: [tpi2-2]

TASK [Point u-boot-update at the recovery partition] ***********************************************************************************************************************
ok: [tpi2-2]

TASK [Label the recovery boot entries] *************************************************************************************************************************************
changed: [tpi2-2]

TASK [Disable cloud-init in the recovery OS] *******************************************************************************************************************************
changed: [tpi2-2]

TASK [Mark the recovery OS] ************************************************************************************************************************************************
changed: [tpi2-2]

TASK [Remove the golden marker from the recovery OS (it belongs to main)] **************************************************************************************************
changed: [tpi2-2]

TASK [Disable lab services in the recovery OS] *****************************************************************************************************************************
changed: [tpi2-2] => (item=docker.socket)
changed: [tpi2-2] => (item=docker.service)
changed: [tpi2-2] => (item=containerd.service)
changed: [tpi2-2] => (item=alloy.service)
ok: [tpi2-2] => (item=k3s.service)
ok: [tpi2-2] => (item=k3s-agent.service)
ok: [tpi2-2] => (item=unattended-upgrades.service)
changed: [tpi2-2] => (item=apt-daily.timer)
changed: [tpi2-2] => (item=apt-daily-upgrade.timer)

TASK [Leave the boot switch DISABLED] **************************************************************************************************************************************
changed: [tpi2-2]

TASK [Verify the recovery tree] ********************************************************************************************************************************************
ok: [tpi2-2]

TASK [Unmount the recovery partition] **************************************************************************************************************************************
changed: [tpi2-2]

TASK [Report (journal this)] ***********************************************************************************************************************************************
ok: [tpi2-2] => {
    "msg": "tpi2-2: recovery=10d87b41-65ae-43c1-98c8-6fb202f3bfcc data=9344303b-2e04-4e0d-8731-85e787a7c021 main=ad692498-9c48-4e70-a1b1-368301614a6f; boot switch disabled. Next: reset.yaml --tags to-recovery."
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-2                     : ok=33   changed=15   unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-2 --tags to-recovery

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-2]

TASK [Mount recovery partition (from main OS)] *****************************************************************************************************************************
changed: [tpi2-2]

TASK [Check recovery extlinux state] ***************************************************************************************************************************************
ok: [tpi2-2]

TASK [Assert recovery extlinux exists (enabled or disabled)] ***************************************************************************************************************
ok: [tpi2-2]

TASK [Enable recovery boot (rename extlinux.conf into place)] **************************************************************************************************************
changed: [tpi2-2]

TASK [Unmount recovery partition] ******************************************************************************************************************************************
changed: [tpi2-2]

TASK [Reboot into recovery OS (NVMe wins the boot scan)] *******************************************************************************************************************
changed: [tpi2-2]

TASK [Confirm recovery OS (root on NVMe, eMMC root unmounted)] *************************************************************************************************************
ok: [tpi2-2]

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-2                     : ok=8    changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

$ ./capture-golden.sh tpi2-2 10.0.0.72
Warning: Permanently added '10.0.0.72' (ED25519) to the list of known hosts.
Warning: Permanently added '10.0.0.72' (ED25519) to the list of known hosts.
capturing /dev/mmcblk0p2 on 10.0.0.72 -> /data/golden/rootfs.img.zst
Warning: Permanently added '10.0.0.72' (ED25519) to the list of known hosts.
30970740736 bytes (31 GB, 29 GiB) copied, 123 s, 252 MB/s
7449+1 records in
7449+1 records out
31247547904 bytes (31 GB, 29 GiB) copied, 127.355 s, 245 MB/s
/*stdin*\            : 11.04%   (  29.1 GiB =>   3.21 GiB, /data/golden/rootfs.img.zst.new) 
rootfs.img.zst: OK
Warning: Permanently added '10.0.0.72' (ED25519) to the list of known hosts.
total 3.3G
-rw-r--r-- 1 root root 3.3G Oct 11 02:15 rootfs.img.zst
-rw-r--r-- 1 root root   81 Oct 11 02:15 rootfs.sha256
captured. Record image identity in the journal:
Warning: Permanently added '10.0.0.72' (ED25519) to the list of known hosts.
5be343c326bac717daa4befeeb2f0786fe1584e4b21b408537cc055a20436be3  rootfs.img.zst
$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-2 --tags to-main,verify

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-2]

TASK [Disable recovery boot (recovery renames its own extlinux)] ***********************************************************************************************************
changed: [tpi2-2]

TASK [Reboot into restored main OS (scan falls through to eMMC)] ***********************************************************************************************************
changed: [tpi2-2]

TASK [Verify main OS booted from eMMC] *************************************************************************************************************************************
ok: [tpi2-2]

TASK [Read golden image provenance marker] *********************************************************************************************************************************
ok: [tpi2-2]

TASK [Report reset provenance (journal this)] ******************************************************************************************************************************
ok: [tpi2-2] => {
    "msg": "tpi2-2 restored to golden: tpi2-2 2026-10-11T01:34:04Z phase-0 baseline"
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-2                     : ok=6    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-2

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-2]

TASK [Mount recovery partition (from main OS)] *****************************************************************************************************************************
changed: [tpi2-2]

TASK [Check recovery extlinux state] ***************************************************************************************************************************************
ok: [tpi2-2]

TASK [Assert recovery extlinux exists (enabled or disabled)] ***************************************************************************************************************
ok: [tpi2-2]

TASK [Enable recovery boot (rename extlinux.conf into place)] **************************************************************************************************************
changed: [tpi2-2]

TASK [Unmount recovery partition] ******************************************************************************************************************************************
changed: [tpi2-2]

TASK [Reboot into recovery OS (NVMe wins the boot scan)] *******************************************************************************************************************
changed: [tpi2-2]

TASK [Confirm recovery OS (root on NVMe, eMMC root unmounted)] *************************************************************************************************************
ok: [tpi2-2]

TASK [Verify golden image checksum] ****************************************************************************************************************************************
ok: [tpi2-2]

TASK [Restore golden image onto eMMC root partition] ***********************************************************************************************************************
changed: [tpi2-2]

TASK [Run filesystem check on restored root] *******************************************************************************************************************************
ok: [tpi2-2]

TASK [Mount restored root and confirm it is bootable] **********************************************************************************************************************
changed: [tpi2-2]

TASK [Confirm restored extlinux.conf present on main root] *****************************************************************************************************************
ok: [tpi2-2]

TASK [Unmount restored root] ***********************************************************************************************************************************************
changed: [tpi2-2]

TASK [Disable recovery boot (recovery renames its own extlinux)] ***********************************************************************************************************
changed: [tpi2-2]

TASK [Reboot into restored main OS (scan falls through to eMMC)] ***********************************************************************************************************
changed: [tpi2-2]

TASK [Verify main OS booted from eMMC] *************************************************************************************************************************************
ok: [tpi2-2]

TASK [Read golden image provenance marker] *********************************************************************************************************************************
ok: [tpi2-2]

TASK [Report reset provenance (journal this)] ******************************************************************************************************************************
ok: [tpi2-2] => {
    "msg": "tpi2-2 restored to golden: tpi2-2 2026-10-11T01:34:04Z phase-0 baseline"
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-2                     : ok=19   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

The node `tpi2-3` needs a postgres reset due to previous defects.

```
$ sudo docker images --digests | grep -E 'postgres|nginx|samba|socat'
alpine/socat    latest    sha256:82ad20f6f6e29b91ff33b6662d24063522b1378f08fd8569cd3ab412cac13f50   82ad20f6f6e2   7 days ago      24.4MB
postgres        16        sha256:1a6ab3f5345eb6dbe04a1349529caabdb0ab09293a09590fad07b2246bfa4b54   1a6ab3f5345e   3 weeks ago     663MB
nginx           1.27      sha256:6784fb0834aa7dbbe12e3d7471e69c290df3e6ba810dc38b34ae33d3c1c05f7d   6784fb0834aa   18 months ago   284MB
dperson/samba   latest    sha256:66088b78a19810dd1457a8f39340e95e663c728083efa5fe7dc0d40b2478e869   66088b78a198   5 years ago     83MB
```

Ansible run for resetting `tpi2-3`

```
$ ansible-playbook -i inventory.yaml --vault-password-file ../.vault-pass site.yaml

PLAY [Deploy protected workloads] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Install Docker Engine and compose plugin] ****************************************************************************************************************************
ok: [tpi2-3]

TASK [Enable and start Docker] *********************************************************************************************************************************************
ok: [tpi2-3]

TASK [Create directories] **************************************************************************************************************************************************
changed: [tpi2-3] => (item=/opt/workloads)
changed: [tpi2-3] => (item=/opt/workloads/www)
changed: [tpi2-3] => (item=/opt/workloads/share)

TASK [Intranet web content] ************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Seed file share] *****************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Template database init (per-role users and grants)] ******************************************************************************************************************
changed: [tpi2-3]

TASK [Template compose file] ***********************************************************************************************************************************************
changed: [tpi2-3]

TASK [Start workloads] *****************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Verify intranet web responds] ****************************************************************************************************************************************
ok: [tpi2-3]

TASK [Verify postgres accepts connections] *********************************************************************************************************************************
FAILED - RETRYING: [tpi2-3]: Verify postgres accepts connections (5 retries left).
ok: [tpi2-3]

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-3                     : ok=11   changed=6    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

There was a failure that needed to be fixed related to permissions. Phase 0 most likely never had these roles either. Its deploy checked only pg_isready, and the file permissions were the same. Any phase-0 note that says the workloads were verified should be read in that light.

`tpi2-3` Ansible run with additional checks.
```
$ ansible-playbook -i inventory.yaml --vault-password-file ../.vault-pass site.yaml

PLAY [Deploy protected workloads] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Install Docker Engine and compose plugin] ****************************************************************************************************************************
ok: [tpi2-3]

TASK [Enable and start Docker] *********************************************************************************************************************************************
ok: [tpi2-3]

TASK [Create directories] **************************************************************************************************************************************************
changed: [tpi2-3] => (item=/opt/workloads)
changed: [tpi2-3] => (item=/opt/workloads/www)
changed: [tpi2-3] => (item=/opt/workloads/share)

TASK [Intranet web content] ************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Seed file share] *****************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Template database init (per-role users and grants)] ******************************************************************************************************************
changed: [tpi2-3]

TASK [Template compose file] ***********************************************************************************************************************************************
changed: [tpi2-3]

TASK [Start workloads] *****************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Verify intranet web responds] ****************************************************************************************************************************************
ok: [tpi2-3]

TASK [Verify postgres accepts connections] *********************************************************************************************************************************
FAILED - RETRYING: [tpi2-3]: Verify postgres accepts connections (5 retries left).
ok: [tpi2-3]

TASK [Verify init.sql ran (roles exist, CONNECT matches the access model)] *************************************************************************************************
ok: [tpi2-3]

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-3                     : ok=12   changed=6    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Verification that the grants exist in the postgres database.

```
$ ssh tpi2-3 "sudo docker exec workloads-postgres-1 psql -U postgres -d labdb -tAc \"
>   SELECT r, has_database_privilege(r, 'labdb', 'CONNECT')
>   FROM unnest(array['remote-admin','remote-developer','remote-analyst','remote-contractor']) r\""
remote-admin|t
remote-developer|t
remote-analyst|t
remote-contractor|f
```

Setting up recovery for `tpi2-3`

```
$ ansible-playbook -i inventory.yaml setup-recovery.yaml -l tpi2-3 -e confirm_wipe_nvme=yes

PLAY [Set up recovery OS and data partition] *******************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Require explicit confirmation (erases the NVMe)] *********************************************************************************************************************
ok: [tpi2-3]

TASK [Read NVMe partition layout] ******************************************************************************************************************************************
ok: [tpi2-3]

TASK [Classify the layout] *************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Classify the layout (already set up?)] *******************************************************************************************************************************
ok: [tpi2-3]

TASK [Already set up, nothing to do] ***************************************************************************************************************************************
skipping: [tpi2-3]

TASK [Skip a node that is already set up] **********************************************************************************************************************************
skipping: [tpi2-3]

TASK [Require the factory layout (one whole-disk partition on /data)] ******************************************************************************************************
ok: [tpi2-3] => {
    "changed": false,
    "msg": "All assertions passed"
}

TASK [Require the main OS (root on the eMMC)] ******************************************************************************************************************************
ok: [tpi2-3]

TASK [Install tools (partitioning, clone, capture)] ************************************************************************************************************************
ok: [tpi2-3]

TASK [Measure data on /data (excluding lost+found)] ************************************************************************************************************************
ok: [tpi2-3]

TASK [Refuse to erase a non-empty /data] ***********************************************************************************************************************************
ok: [tpi2-3]

TASK [Refuse if a process is using /data] **********************************************************************************************************************************
ok: [tpi2-3]

TASK [Unmount any stray recovery mount] ************************************************************************************************************************************
ok: [tpi2-3]

TASK [Unmount /data and drop its old fstab entry] **************************************************************************************************************************
changed: [tpi2-3]

TASK [Wipe and repartition the NVMe] ***************************************************************************************************************************************
changed: [tpi2-3]

TASK [Create filesystems] **************************************************************************************************************************************************
changed: [tpi2-3] => (item={'dev': '/dev/nvme0n1p1', 'label': 'recovery'})
changed: [tpi2-3] => (item={'dev': '/dev/nvme0n1p2', 'label': 'data'})

TASK [Read filesystem UUIDs] ***********************************************************************************************************************************************
ok: [tpi2-3] => (item=/dev/nvme0n1p1)
ok: [tpi2-3] => (item=/dev/nvme0n1p2)
ok: [tpi2-3] => (item=/dev/mmcblk0p2)

TASK [Record UUIDs] ********************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Mount the new /data by UUID (nofail)] ********************************************************************************************************************************
changed: [tpi2-3]

TASK [Write the golden-image provenance marker on main (if absent)] ********************************************************************************************************
changed: [tpi2-3]

TASK [Mount the recovery partition (ephemeral)] ****************************************************************************************************************************
changed: [tpi2-3]

TASK [Clone the main root into the recovery partition] *********************************************************************************************************************
changed: [tpi2-3]

TASK [Point the recovery root and boot entry at the recovery partition] ****************************************************************************************************
changed: [tpi2-3] => (item=/etc/fstab)
changed: [tpi2-3] => (item=/boot/extlinux/extlinux.conf)

TASK [Check for u-boot-update defaults in the recovery OS] *****************************************************************************************************************
ok: [tpi2-3]

TASK [Point u-boot-update at the recovery partition] ***********************************************************************************************************************
ok: [tpi2-3]

TASK [Label the recovery boot entries] *************************************************************************************************************************************
changed: [tpi2-3]

TASK [Disable cloud-init in the recovery OS] *******************************************************************************************************************************
changed: [tpi2-3]

TASK [Mark the recovery OS] ************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Remove the golden marker from the recovery OS (it belongs to main)] **************************************************************************************************
changed: [tpi2-3]

TASK [Disable lab services in the recovery OS] *****************************************************************************************************************************
changed: [tpi2-3] => (item=docker.socket)
changed: [tpi2-3] => (item=docker.service)
changed: [tpi2-3] => (item=containerd.service)
changed: [tpi2-3] => (item=alloy.service)
ok: [tpi2-3] => (item=k3s.service)
ok: [tpi2-3] => (item=k3s-agent.service)
ok: [tpi2-3] => (item=unattended-upgrades.service)
changed: [tpi2-3] => (item=apt-daily.timer)
changed: [tpi2-3] => (item=apt-daily-upgrade.timer)

TASK [Leave the boot switch DISABLED] **************************************************************************************************************************************
changed: [tpi2-3]

TASK [Verify the recovery tree] ********************************************************************************************************************************************
ok: [tpi2-3]

TASK [Unmount the recovery partition] **************************************************************************************************************************************
changed: [tpi2-3]

TASK [Report (journal this)] ***********************************************************************************************************************************************
ok: [tpi2-3] => {
    "msg": "tpi2-3: recovery=4e08b598-3412-47c4-9b11-66068edac57e data=4bf0d8bb-be97-4c71-b498-1d70c984721d main=ad692498-9c48-4e70-a1b1-368301614a6f; boot switch disabled. Next: reset.yaml --tags to-recovery."
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-3                     : ok=33   changed=15   unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   

$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-3 --tags to-recovery

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Read NVMe partition labels] ******************************************************************************************************************************************
ok: [tpi2-3]

TASK [Require the node-reset layout (recovery + data partitions)] **********************************************************************************************************
ok: [tpi2-3]

TASK [Mount recovery partition (from main OS)] *****************************************************************************************************************************
changed: [tpi2-3]

TASK [Check recovery extlinux state] ***************************************************************************************************************************************
ok: [tpi2-3]

TASK [Assert recovery extlinux exists (enabled or disabled)] ***************************************************************************************************************
ok: [tpi2-3]

TASK [Enable recovery boot (rename extlinux.conf into place)] **************************************************************************************************************
changed: [tpi2-3]

TASK [Unmount recovery partition] ******************************************************************************************************************************************
changed: [tpi2-3]

TASK [Reboot into recovery OS (NVMe wins the boot scan)] *******************************************************************************************************************
changed: [tpi2-3]

TASK [Confirm recovery OS (root on NVMe, eMMC root unmounted)] *************************************************************************************************************
ok: [tpi2-3]

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-3                     : ok=10   changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

$ ./capture-golden.sh tpi2-3 10.0.0.73
capturing /dev/mmcblk0p2 on 10.0.0.73 -> /data/golden/rootfs.img.zst
31117541376 bytes (31 GB, 29 GiB) copied, 124 s, 251 MB/s
7449+1 records in
7449+1 records out
31247547904 bytes (31 GB, 29 GiB) copied, 127.977 s, 244 MB/s
/*stdin*\            :  9.47%   (  29.1 GiB =>   2.76 GiB, /data/golden/rootfs.img.zst.new) 
rootfs.img.zst: OK
Warning: Permanently added '10.0.0.73' (ED25519) to the list of known hosts.
total 2.8G
-rw-r--r-- 1 root root 2.8G Oct 11 02:35 rootfs.img.zst
-rw-r--r-- 1 root root   81 Oct 11 02:35 rootfs.sha256
captured. Record image identity in the journal:
51afc56aea8cceab90d15c0473bd41e80a46c64acaefb13ba5ac0ab342fb1019  rootfs.img.zst
$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-3 --tags to-main,verify

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Read NVMe partition labels] ******************************************************************************************************************************************
ok: [tpi2-3]

TASK [Require the node-reset layout (recovery + data partitions)] **********************************************************************************************************
ok: [tpi2-3]

TASK [Disable recovery boot (recovery renames its own extlinux)] ***********************************************************************************************************
changed: [tpi2-3]

TASK [Reboot into restored main OS (scan falls through to eMMC)] ***********************************************************************************************************
changed: [tpi2-3]

TASK [Verify main OS booted from eMMC] *************************************************************************************************************************************
ok: [tpi2-3]

TASK [Read golden image provenance marker] *********************************************************************************************************************************
ok: [tpi2-3]

TASK [Report reset provenance (journal this)] ******************************************************************************************************************************
ok: [tpi2-3] => {
    "msg": "tpi2-3 restored to golden: tpi2-3 2026-10-11T02:29:50Z phase-0 baseline"
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-3                     : ok=8    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

$ ansible-playbook -i inventory.yaml reset.yaml -l tpi2-3

PLAY [Reset node to golden state] ******************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Read NVMe partition labels] ******************************************************************************************************************************************
ok: [tpi2-3]

TASK [Require the node-reset layout (recovery + data partitions)] **********************************************************************************************************
ok: [tpi2-3]

TASK [Mount recovery partition (from main OS)] *****************************************************************************************************************************
changed: [tpi2-3]

TASK [Check recovery extlinux state] ***************************************************************************************************************************************
ok: [tpi2-3]

TASK [Assert recovery extlinux exists (enabled or disabled)] ***************************************************************************************************************
ok: [tpi2-3]

TASK [Enable recovery boot (rename extlinux.conf into place)] **************************************************************************************************************
changed: [tpi2-3]

TASK [Unmount recovery partition] ******************************************************************************************************************************************
changed: [tpi2-3]

TASK [Reboot into recovery OS (NVMe wins the boot scan)] *******************************************************************************************************************
changed: [tpi2-3]

TASK [Confirm recovery OS (root on NVMe, eMMC root unmounted)] *************************************************************************************************************
ok: [tpi2-3]

TASK [Verify golden image checksum] ****************************************************************************************************************************************
ok: [tpi2-3]

TASK [Restore golden image onto eMMC root partition] ***********************************************************************************************************************
changed: [tpi2-3]

TASK [Run filesystem check on restored root] *******************************************************************************************************************************
ok: [tpi2-3]

TASK [Mount restored root and confirm it is bootable] **********************************************************************************************************************
changed: [tpi2-3]

TASK [Confirm restored extlinux.conf present on main root] *****************************************************************************************************************
ok: [tpi2-3]

TASK [Unmount restored root] ***********************************************************************************************************************************************
changed: [tpi2-3]

TASK [Disable recovery boot (recovery renames its own extlinux)] ***********************************************************************************************************
changed: [tpi2-3]

TASK [Reboot into restored main OS (scan falls through to eMMC)] ***********************************************************************************************************
changed: [tpi2-3]

TASK [Verify main OS booted from eMMC] *************************************************************************************************************************************
ok: [tpi2-3]

TASK [Read golden image provenance marker] *********************************************************************************************************************************
ok: [tpi2-3]

TASK [Report reset provenance (journal this)] ******************************************************************************************************************************
ok: [tpi2-3] => {
    "msg": "tpi2-3 restored to golden: tpi2-3 2026-10-11T02:29:50Z phase-0 baseline"
}

PLAY RECAP *****************************************************************************************************************************************************************
tpi2-3                     : ok=21   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Now that the nodes are all setup properly for testing, run the ansible playbook for `openvpn`

```
$ LAB_VPN_ENDPOINT=$(curl -4 -s https://checkip.amazonaws.com) ansible-playbook -i inventory.yaml openvpn.yaml

PLAY [Deploy the site-to-site hub on the AWS VPN gateway] ******************************************************************************************************************

TASK [Require the hub's Elastic IP] ****************************************************************************************************************************************
ok: [aws-vpn-gateway]

TASK [Gather facts] ********************************************************************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Warn about deprecated openvpn_ci_build usage] ********************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Fail if both IPv4 and IPv6 tunnel networks are disabled] *********************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Initialize long client CNs list] *********************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Collect clients with CN exceeding 64 characters] *****************************************************************************************
skipping: [aws-vpn-gateway] => (item=tpi2-4) 
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Assert CA CN length (strict mode)] *******************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Assert server CN length (strict mode)] ***************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Fail if any client CN too long (strict mode)] ********************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Warn if CA CN exceeds 64 chars (warning mode)] *******************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Warn if server CN exceeds 64 chars (warning mode)] ***************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : validate | Warn about long client CNs (warning mode)] ***********************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : Include vars for OpenVPN installation] **************************************************************************************************************
ok: [aws-vpn-gateway] => (item=/Users/<user>/.ansible/roles/kyl191.openvpn/vars/os/Debian.yml)

TASK [kyl191.openvpn : uninstall | Disable openvpn auto-start & start] *****************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : uninstall | Wipe out config directory] **************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : uninstall | Remove openvpn logrotate config file] ***************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : uninstall | Uninstall OpenVPN] **********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : uninstall | Uninstall LDAP plugin] ******************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : uninstall | Terminate playbook] *********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Install EPEL for CentOS-like distros] *****************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Install EPEL for RHEL] ********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Gather the installed packages] ************************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Ensure packages fact exists] **************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Refresh apt cache] ************************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Install openvpn] **************************************************************************************************************************
changed: [aws-vpn-gateway] => (item=openvpn)
ok: [aws-vpn-gateway] => (item=openssl)

TASK [kyl191.openvpn : install | Install LDAP plugin] **********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Install selinux dependencies (RedHat)] ****************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Install selinux dependencies (Debian/Ubuntu)] *********************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Check if CRB repository is enabled] *******************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Enable CRB repository for CentOS 10-like distros] *****************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : install | Ensure group 'nogroup' is present] ********************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Create openvpn key directory] *********************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Copy openssl server/ca extensions] ****************************************************************************************************
changed: [aws-vpn-gateway] => (item=openssl-server.ext)
changed: [aws-vpn-gateway] => (item=openssl-ca.ext)

TASK [kyl191.openvpn : server_keys | Copy CA key] **************************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Copy CA cert] *************************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Generate CA key] **********************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Protect CA key] ***********************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Sign CA key] **************************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Generate server key] ******************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Protect server key] *******************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Sign server key] **********************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Copy tls-auth key] ********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Generate tls-auth key] ****************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Copy tls-crypt key] *******************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Generate tls-crypt key] ***************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Copy pre-generated DH params] *********************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Generate dh params] *******************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Install ca.conf config file] **********************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys | Setup Certificate Revocation List] ****************************************************************************************************
included: /Users/<user>/.ansible/roles/kyl191.openvpn/tasks/server_keys_crl.yml for aws-vpn-gateway

TASK [kyl191.openvpn : server_keys_crl | Create initial certificate revocation list squence number] ************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys_crl | Install revocation script] ********************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys_crl | Check if certificate revocation list database exists] *****************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys_crl | Create certificate revocation list database if required] **************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys_crl | Set up certificate revocation list] ***********************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys_crl | Install crl-cron script] **********************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys_crl | Install crl-cron service] *********************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys_crl | Install crl-cron systemd timer] ***************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys_crl | Activate systemd timer to check daily if the CRL needs to be renewed] *************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : server_keys_crl | Fail if there's no systemd] *******************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : Enable ipv4 forwarding] *****************************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : Enable ipv6 forwarding] *****************************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | firewall | Fail on both firewalld & ufw] *************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | firewall | Fail on no firewall detected] *************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | firewall | Determine firewall backend] ***************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | firewall | Fail if IPv4 SNAT is needed but no default IPv4 route exists] *****************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | firewall | Fail if IPv6 SNAT is needed but no default IPv6 route exists] *****************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | firewall | Add port rules (iptables)] ****************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | firewall | Add port rules (firewalld)] ***************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | firewall | Add port rules (ufw)] *********************************************************************************************************
included: /Users/<user>/.ansible/roles/kyl191.openvpn/tasks/firewall/ufw.yml for aws-vpn-gateway

TASK [kyl191.openvpn : firewall | ufw | Start ufw service] *****************************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | ufw | Enable ufw] ************************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | ufw | Enable forwarding] *****************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | ufw | Allow incoming VPN connections] ****************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | ufw | Accept packets from VPN tunnel adaptor] ********************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | ufw | Setup IPv4 SNAT rules] *************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | ufw | Setup IPv6 SNAT rules] *************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | ufw | Setup IPv4 NAT with MASQUERADE] ****************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : firewall | ufw | Setup IPv6 NAT with MASQUERADE] ****************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Allow OpenVPN port (semanage)] ************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Check if legacy module is loaded] *********************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Remove legacy module] *********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Remove legacy module files] ***************************************************************************************************************
skipping: [aws-vpn-gateway] => (item=my-openvpn-server.te) 
skipping: [aws-vpn-gateway] => (item=my-openvpn-server.mod) 
skipping: [aws-vpn-gateway] => (item=my-openvpn-server.pp) 
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Warn about deprecated module method] ******************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Check if module was loaded] ***************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Copy selinux type enforcement file] *******************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Make sure selinux policy build RPM is installed] ******************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Install selinux-policy-targeted-extra for RHEL 10 and variants] ***************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : selinux | Build and install selinux policy] *********************************************************************************************************
skipping: [aws-vpn-gateway] => (item=checkmodule -M -m -o my-openvpn-server.mod my-openvpn-server.te) 
skipping: [aws-vpn-gateway] => (item=semodule_package -o my-openvpn-server.pp -m my-openvpn-server.mod) 
skipping: [aws-vpn-gateway] => (item=semodule -i my-openvpn-server.pp) 
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : cert_sync_detection | Get existing certs] ***********************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : cert_sync_detection | Create list of existing client with existing certs] ***************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : cert_sync_detection | Create list of cert to revoke] ************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : cert_sync_detection | Debug: Certs to revoke (skipped if none)] *************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : client_keys | Create openvpn ovpn file directory] ***************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : client_keys | Copy openssl client extensions] *******************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : client_keys | Generate client key] ******************************************************************************************************************
changed: [aws-vpn-gateway] => (item=tpi2-4)

TASK [kyl191.openvpn : client_keys | Protect client keys] ******************************************************************************************************************
changed: [aws-vpn-gateway] => (item=tpi2-4)

TASK [kyl191.openvpn : client_keys | Sign client key] **********************************************************************************************************************
changed: [aws-vpn-gateway] => (item=tpi2-4)

TASK [kyl191.openvpn : client_keys | Register server ca key] ***************************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : client_keys | Register tls-auth key] ****************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : client_keys | Register tls-crypt key] ***************************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : client_keys | Register client certs] ****************************************************************************************************************
ok: [aws-vpn-gateway] => (item=tpi2-4)

TASK [kyl191.openvpn : client_keys | Register client keys] *****************************************************************************************************************
ok: [aws-vpn-gateway] => (item=tpi2-4)

TASK [kyl191.openvpn : client_keys | Generate client config] ***************************************************************************************************************
changed: [aws-vpn-gateway] => (item=(censored due to no_log))

TASK [kyl191.openvpn : client_keys | Fetch client config] ******************************************************************************************************************
changed: [aws-vpn-gateway] => (item=tpi2-4)

TASK [kyl191.openvpn : revocation | Remove client config] ******************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : revocation | Revoke certificates] *******************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : revocation | Remove client key] *********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : revocation | Remove client csr] *********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : revocation | Remove client cert] ********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Create openvpn config file] ****************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Copy up script if defined] *****************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Copy down script if defined] ***************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Copy client-connect script if defined] *****************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Copy client-disconnect script if defined] **************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Ensure auth folder exist in openvpn dir] ***************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Delete auth folder in openvpn dir] *********************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Install LDAP config] ***********************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Create log directory] **********************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Copy openvpn logrotate config file] ********************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Create client config directory] ************************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Create client configs] *********************************************************************************************************************
changed: [aws-vpn-gateway] => (item={'key': 'tpi2-4', 'value': ['iroute 10.0.0.0 255.255.255.0']})

TASK [kyl191.openvpn : config | List client config directory] **************************************************************************************************************
ok: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Delete undeclared configs in client config directory] **************************************************************************************
skipping: [aws-vpn-gateway] => (item=tpi2-4) 
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Delete client config directory] ************************************************************************************************************
skipping: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Create openvpn service override directory] *************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Copy openvpn service override file] ********************************************************************************************************
changed: [aws-vpn-gateway]

TASK [kyl191.openvpn : config | Setup openvpn auto-start & start] **********************************************************************************************************
changed: [aws-vpn-gateway]

RUNNING HANDLER [kyl191.openvpn : Restart openvpn] *************************************************************************************************************************
changed: [aws-vpn-gateway]

RUNNING HANDLER [kyl191.openvpn : Restart ufw] *****************************************************************************************************************************
changed: [aws-vpn-gateway]

PLAY [Deploy perimeter-baseline OpenVPN server] ****************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************
ok: [tpi2-4]

TASK [Require the public endpoint remote workers dial] *********************************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : validate | Warn about deprecated openvpn_ci_build usage] ********************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : validate | Fail if both IPv4 and IPv6 tunnel networks are disabled] *********************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : validate | Initialize long client CNs list] *********************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : validate | Collect clients with CN exceeding 64 characters] *****************************************************************************************
skipping: [tpi2-4] => (item=remote-admin) 
skipping: [tpi2-4] => (item=remote-developer) 
skipping: [tpi2-4] => (item=remote-analyst) 
skipping: [tpi2-4] => (item=remote-contractor) 
skipping: [tpi2-4]

TASK [kyl191.openvpn : validate | Assert CA CN length (strict mode)] *******************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : validate | Assert server CN length (strict mode)] ***************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : validate | Fail if any client CN too long (strict mode)] ********************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : validate | Warn if CA CN exceeds 64 chars (warning mode)] *******************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : validate | Warn if server CN exceeds 64 chars (warning mode)] ***************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : validate | Warn about long client CNs (warning mode)] ***********************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : Include vars for OpenVPN installation] **************************************************************************************************************
ok: [tpi2-4] => (item=/Users/<user>/.ansible/roles/kyl191.openvpn/vars/os/Debian.yml)

TASK [kyl191.openvpn : uninstall | Disable openvpn auto-start & start] *****************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : uninstall | Wipe out config directory] **************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : uninstall | Remove openvpn logrotate config file] ***************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : uninstall | Uninstall OpenVPN] **********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : uninstall | Uninstall LDAP plugin] ******************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : uninstall | Terminate playbook] *********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : install | Install EPEL for CentOS-like distros] *****************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : install | Install EPEL for RHEL] ********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : install | Gather the installed packages] ************************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : install | Ensure packages fact exists] **************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : install | Refresh apt cache] ************************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : install | Install openvpn] **************************************************************************************************************************
changed: [tpi2-4] => (item=openvpn)
ok: [tpi2-4] => (item=openssl)

TASK [kyl191.openvpn : install | Install LDAP plugin] **********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : install | Install selinux dependencies (RedHat)] ****************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : install | Install selinux dependencies (Debian/Ubuntu)] *********************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : install | Check if CRB repository is enabled] *******************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : install | Enable CRB repository for CentOS 10-like distros] *****************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : install | Ensure group 'nogroup' is present] ********************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Create openvpn key directory] *********************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Copy openssl server/ca extensions] ****************************************************************************************************
changed: [tpi2-4] => (item=openssl-server.ext)
changed: [tpi2-4] => (item=openssl-ca.ext)

TASK [kyl191.openvpn : server_keys | Copy CA key] **************************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Copy CA cert] *************************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Generate CA key] **********************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Protect CA key] ***********************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Sign CA key] **************************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Generate server key] ******************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Protect server key] *******************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Sign server key] **********************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Copy tls-auth key] ********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Generate tls-auth key] ****************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Copy tls-crypt key] *******************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Generate tls-crypt key] ***************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Copy pre-generated DH params] *********************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Generate dh params] *******************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Install ca.conf config file] **********************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys | Setup Certificate Revocation List] ****************************************************************************************************
included: /Users/<user>/.ansible/roles/kyl191.openvpn/tasks/server_keys_crl.yml for tpi2-4

TASK [kyl191.openvpn : server_keys_crl | Create initial certificate revocation list squence number] ************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys_crl | Install revocation script] ********************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys_crl | Check if certificate revocation list database exists] *****************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : server_keys_crl | Create certificate revocation list database if required] **************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys_crl | Set up certificate revocation list] ***********************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys_crl | Install crl-cron script] **********************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys_crl | Install crl-cron service] *********************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys_crl | Install crl-cron systemd timer] ***************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys_crl | Activate systemd timer to check daily if the CRL needs to be renewed] *************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : server_keys_crl | Fail if there's no systemd] *******************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : Enable ipv4 forwarding] *****************************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : Enable ipv6 forwarding] *****************************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : firewall | firewall | Fail on both firewalld & ufw] *************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : firewall | firewall | Fail on no firewall detected] *************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : firewall | firewall | Determine firewall backend] ***************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : firewall | firewall | Fail if IPv4 SNAT is needed but no default IPv4 route exists] *****************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : firewall | firewall | Fail if IPv6 SNAT is needed but no default IPv6 route exists] *****************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : firewall | firewall | Add port rules (iptables)] ****************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : firewall | firewall | Add port rules (firewalld)] ***************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : firewall | firewall | Add port rules (ufw)] *********************************************************************************************************
included: /Users/<user>/.ansible/roles/kyl191.openvpn/tasks/firewall/ufw.yml for tpi2-4

TASK [kyl191.openvpn : firewall | ufw | Start ufw service] *****************************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : firewall | ufw | Enable ufw] ************************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : firewall | ufw | Enable forwarding] *****************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : firewall | ufw | Allow incoming VPN connections] ****************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : firewall | ufw | Accept packets from VPN tunnel adaptor] ********************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : firewall | ufw | Setup IPv4 SNAT rules] *************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : firewall | ufw | Setup IPv6 SNAT rules] *************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : firewall | ufw | Setup IPv4 NAT with MASQUERADE] ****************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : firewall | ufw | Setup IPv6 NAT with MASQUERADE] ****************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Allow OpenVPN port (semanage)] ************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Check if legacy module is loaded] *********************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Remove legacy module] *********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Remove legacy module files] ***************************************************************************************************************
skipping: [tpi2-4] => (item=my-openvpn-server.te) 
skipping: [tpi2-4] => (item=my-openvpn-server.mod) 
skipping: [tpi2-4] => (item=my-openvpn-server.pp) 
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Warn about deprecated module method] ******************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Check if module was loaded] ***************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Copy selinux type enforcement file] *******************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Make sure selinux policy build RPM is installed] ******************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Install selinux-policy-targeted-extra for RHEL 10 and variants] ***************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : selinux | Build and install selinux policy] *********************************************************************************************************
skipping: [tpi2-4] => (item=checkmodule -M -m -o my-openvpn-server.mod my-openvpn-server.te) 
skipping: [tpi2-4] => (item=semodule_package -o my-openvpn-server.pp -m my-openvpn-server.mod) 
skipping: [tpi2-4] => (item=semodule -i my-openvpn-server.pp) 
skipping: [tpi2-4]

TASK [kyl191.openvpn : cert_sync_detection | Get existing certs] ***********************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : cert_sync_detection | Create list of existing client with existing certs] ***************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : cert_sync_detection | Create list of cert to revoke] ************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : cert_sync_detection | Debug: Certs to revoke (skipped if none)] *************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : client_keys | Create openvpn ovpn file directory] ***************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : client_keys | Copy openssl client extensions] *******************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : client_keys | Generate client key] ******************************************************************************************************************
changed: [tpi2-4] => (item=remote-admin)
changed: [tpi2-4] => (item=remote-developer)
changed: [tpi2-4] => (item=remote-analyst)
changed: [tpi2-4] => (item=remote-contractor)

TASK [kyl191.openvpn : client_keys | Protect client keys] ******************************************************************************************************************
changed: [tpi2-4] => (item=remote-admin)
changed: [tpi2-4] => (item=remote-developer)
changed: [tpi2-4] => (item=remote-analyst)
changed: [tpi2-4] => (item=remote-contractor)

TASK [kyl191.openvpn : client_keys | Sign client key] **********************************************************************************************************************
changed: [tpi2-4] => (item=remote-admin)
changed: [tpi2-4] => (item=remote-developer)
changed: [tpi2-4] => (item=remote-analyst)
changed: [tpi2-4] => (item=remote-contractor)

TASK [kyl191.openvpn : client_keys | Register server ca key] ***************************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : client_keys | Register tls-auth key] ****************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : client_keys | Register tls-crypt key] ***************************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : client_keys | Register client certs] ****************************************************************************************************************
ok: [tpi2-4] => (item=remote-admin)
ok: [tpi2-4] => (item=remote-developer)
ok: [tpi2-4] => (item=remote-analyst)
ok: [tpi2-4] => (item=remote-contractor)

TASK [kyl191.openvpn : client_keys | Register client keys] *****************************************************************************************************************
ok: [tpi2-4] => (item=remote-admin)
ok: [tpi2-4] => (item=remote-developer)
ok: [tpi2-4] => (item=remote-analyst)
ok: [tpi2-4] => (item=remote-contractor)

TASK [kyl191.openvpn : client_keys | Generate client config] ***************************************************************************************************************
changed: [tpi2-4] => (item=(censored due to no_log))
changed: [tpi2-4] => (item=(censored due to no_log))
changed: [tpi2-4] => (item=(censored due to no_log))
changed: [tpi2-4] => (item=(censored due to no_log))

TASK [kyl191.openvpn : client_keys | Fetch client config] ******************************************************************************************************************
changed: [tpi2-4] => (item=remote-admin)
changed: [tpi2-4] => (item=remote-developer)
changed: [tpi2-4] => (item=remote-analyst)
changed: [tpi2-4] => (item=remote-contractor)

TASK [kyl191.openvpn : revocation | Remove client config] ******************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : revocation | Revoke certificates] *******************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : revocation | Remove client key] *********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : revocation | Remove client csr] *********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : revocation | Remove client cert] ********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : config | Create openvpn config file] ****************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : config | Copy up script if defined] *****************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : config | Copy down script if defined] ***************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : config | Copy client-connect script if defined] *****************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : config | Copy client-disconnect script if defined] **************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : config | Ensure auth folder exist in openvpn dir] ***************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : config | Delete auth folder in openvpn dir] *********************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : config | Install LDAP config] ***********************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : config | Create log directory] **********************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : config | Copy openvpn logrotate config file] ********************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : config | Create client config directory] ************************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : config | Create client configs] *********************************************************************************************************************
changed: [tpi2-4] => (item={'key': 'remote-admin', 'value': ['ifconfig-push 10.9.0.17 255.255.255.0']})
changed: [tpi2-4] => (item={'key': 'remote-developer', 'value': ['ifconfig-push 10.9.0.18 255.255.255.0']})
changed: [tpi2-4] => (item={'key': 'remote-analyst', 'value': ['ifconfig-push 10.9.0.19 255.255.255.0']})
changed: [tpi2-4] => (item={'key': 'remote-contractor', 'value': ['ifconfig-push 10.9.0.33 255.255.255.0']})

TASK [kyl191.openvpn : config | List client config directory] **************************************************************************************************************
ok: [tpi2-4]

TASK [kyl191.openvpn : config | Delete undeclared configs in client config directory] **************************************************************************************
skipping: [tpi2-4] => (item=remote-admin) 
skipping: [tpi2-4] => (item=remote-analyst) 
skipping: [tpi2-4] => (item=remote-contractor) 
skipping: [tpi2-4] => (item=remote-developer) 
skipping: [tpi2-4]

TASK [kyl191.openvpn : config | Delete client config directory] ************************************************************************************************************
skipping: [tpi2-4]

TASK [kyl191.openvpn : config | Create openvpn service override directory] *************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : config | Copy openvpn service override file] ********************************************************************************************************
changed: [tpi2-4]

TASK [kyl191.openvpn : config | Setup openvpn auto-start & start] **********************************************************************************************************
changed: [tpi2-4]

RUNNING HANDLER [kyl191.openvpn : Restart openvpn] *************************************************************************************************************************
changed: [tpi2-4]

RUNNING HANDLER [kyl191.openvpn : Restart ufw] *****************************************************************************************************************************
changed: [tpi2-4]

TASK [Perimeter ruleset | allow listed group traffic from the tunnel] ******************************************************************************************************
changed: [tpi2-4] => (item=staff -> on-prem LAN)
changed: [tpi2-4] => (item=staff -> AWS VPC)
changed: [tpi2-4] => (item=contractor -> intranet-web)
changed: [tpi2-4] => (item=contractor -> postgres (db denies))
changed: [tpi2-4] => (item=contractor -> lab DNS)
changed: [tpi2-4] => (item=contractor -> lab DNS (tcp))

TASK [Perimeter ruleset | deny all other routed traffic] *******************************************************************************************************************
changed: [tpi2-4]

TASK [Host firewall | allow SSH and monitoring from the lab LAN] ***********************************************************************************************************
changed: [tpi2-4]

TASK [Host firewall | deny all other inbound (1194/udp and tun0 stay open)] ************************************************************************************************
changed: [tpi2-4]

TASK [Record deployed OpenVPN version (data collection)] *******************************************************************************************************************
ok: [tpi2-4]

TASK [Record the live ruleset (Phase 3 translation input)] *****************************************************************************************************************
ok: [tpi2-4]

TASK [Show version and ruleset for the work journal] ***********************************************************************************************************************
ok: [tpi2-4] => {
    "msg": [
        "OpenVPN 2.6.19 aarch64-unknown-linux-gnu [SSL (OpenSSL)] [LZO] [LZ4] [EPOLL] [PKCS11] [MH/PKTINFO] [AEAD] [DCO]",
        "Status: active",
        "Logging: on (low)",
        "Default: deny (incoming), allow (outgoing), deny (routed)",
        "New profiles: skip",
        "",
        "To                         Action      From",
        "--                         ------      ----",
        "1194/udp                   ALLOW IN    Anywhere                  ",
        "Anywhere on tun0           ALLOW IN    Anywhere                  ",
        "Anywhere                   ALLOW IN    10.0.0.0/24                # lab LAN -> tpi2-4 (ssh, node_exporter)",
        "1194/udp (v6)              ALLOW IN    Anywhere (v6)             ",
        "Anywhere (v6) on tun0      ALLOW IN    Anywhere (v6)             ",
        "",
        "10.0.0.0/24                ALLOW FWD   10.9.0.16/28 on tun0       # staff -> on-prem LAN",
        "10.100.0.0/16              ALLOW FWD   10.9.0.16/28 on tun0       # staff -> AWS VPC",
        "10.0.0.73 8080/tcp         ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> intranet-web",
        "10.0.0.73 5432/tcp         ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> postgres (db denies)",
        "10.0.0.153 53/udp          ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> lab DNS",
        "10.0.0.153 53/tcp          ALLOW FWD   10.9.0.32/28 on tun0       # contractor -> lab DNS (tcp)"
    ]
}

PLAY [Connect tpi2-4 to the AWS site-to-site hub] **************************************************************************************************************************

TASK [Install the site-to-site profile fetched from the hub] ***************************************************************************************************************
changed: [tpi2-4]

TASK [Enable and start the site-to-site tunnel] ****************************************************************************************************************************
changed: [tpi2-4]

TASK [Apply a changed profile now] *****************************************************************************************************************************************

RUNNING HANDLER [Restart site-to-site tunnel] ******************************************************************************************************************************
changed: [tpi2-4]

TASK [Wait for the AWS VPC route through the tunnel] ***********************************************************************************************************************
FAILED - RETRYING: [tpi2-4]: Wait for the AWS VPC route through the tunnel (11 retries left).
ok: [tpi2-4]

TASK [Verify aws-app answers through the tunnel] ***************************************************************************************************************************
ok: [tpi2-4]

PLAY RECAP *****************************************************************************************************************************************************************
aws-vpn-gateway            : ok=63   changed=43   unreachable=0    failed=0    skipped=65   rescued=0    ignored=0   
tpi2-4                     : ok=75   changed=50   unreachable=0    failed=0    skipped=65   rescued=0    ignored=0
```

## 2026-10-11 21:30-22:00 | phase-1 | test-matrix | testing
First Phase 1 access-matrix run for `remote-contractor`
(run `2c154aea8a3c`, `results/phase-1_remote-contractor_20261011T045434Z_2c154aea8a3c.csv`)
is INVALID and excluded from analysis. The CSV is kept as data.

The network-level results were as expected: intranet-web allowed; file-service,
legacy-service and aws-app denied by timeout (the perimeter ruleset dropping
routed traffic). However, the probing machine was incomplete:
- `psql` was not on PATH (Homebrew `libpq` is keg-only), so both postgres rows
  were ERROR.
- No AWS profile existed for the role. The S3 write row recorded "deny"
  because the CLI could not find the profile, and the S3 read row recorded
  "deny" on a timeout. Neither reflects an IAM decision, so both are false passes.

Root cause in the instrument: `exec` probes counted any nonzero exit as deny,
so a misconfigured probing machine scores deny rows as passes. Fixed in the
harness (see the coding entry below). The contractor run will be repeated after
setting up the probe environment (psql on PATH, PGPASSWORD, AWS profiles per
role, LAB_DATA_BUCKET).

## 2026-10-11 22:00-22:45 | phase-1 | test-matrix | coding
Hardened the access-matrix harness before recording Phase 1 results. `exec`
probes now need a deny signature (`deny_pattern`): a nonzero exit counts as a
deny only if its output shows the control refusing (`AccessDenied` for S3;
`permission denied for database|table` or a network-level failure for
postgres). Anything else is ERROR. Added `deny_on_timeout` (false for S3,
which is reached over the internet, not the tunnel) and per-probe `timeout`
(30 s for the aws CLI cold start). Switched the S3 read probe from
head-object to get-object, because HEAD responses carry no error code and
cannot distinguish AccessDenied from an invalid key. Added `psql -w` so a
missing password errors instead of prompting. Added requirements.txt. PyYAML
version installed: 6.0.3.

There are two more results that were part of the setup. They should not be counted.

Created the `results/excluded` for results that are to excluded from data analysis. There was a run for `remote-admin` that produced a probe-creedential error. It's now fixed.

```
phase        role                     pass   fail  error    rate
phase-1      remote-admin                8      0      0  100.0%
phase-1      remote-analyst              8      0      0  100.0%
phase-1      remote-contractor           8      0      0  100.0%
phase-1      remote-developer            8      0      0  100.0%
```

## 2026-10-11 22:45-22:50 | phase-1 | ansible-workloads | coding
Added the perf-battery iperf3 server to the workloads deployment on tpi2-3.
Until now it was started by hand outside version control and was lost on
every reset. ansible-workloads now installs iperf3 non-interactively and
runs it as `lab-iperf3.service` on port 5201 (variable `iperf3_port`). The
service has its own unit name, runs unprivileged (DynamicUser), restarts on
failure and is enabled at boot. A new final check confirms the port accepts
connections from the controller. iperf3 is a measurement target only, not an
access-matrix resource, and is listed that way in the workloads and
perf-battery READMEs. The AWS path is measured for HTTP latency only, because
the app subnet has no internet route and iperf3 cannot be installed there.

## 2026-10-11 22:50-23:10 | phase-1 | node-reset | deployment
Rolled iperf3 into tpi2-3's golden baseline without capturing test data.
1. Full reset of tpi2-3 to the existing golden image. This removed the rows
   and objects written by the Phase 1 access-matrix probes.
2. Re-ran ansible-workloads. iperf3 was added; init.sql did not re-run, since
   pgdata already existed, so grants were unchanged.
3. Recaptured the golden image: to-recovery, capture-golden.sh, then
   to-main and verify.
New tpi2-3 golden sha256: 0008e8f5e4e9a838503b2603da2e30a4300942ec308f81acad6f16584b356533
Capture time: 10:00.
From now on, a reset of tpi2-3 restores the workloads including iperf3.

## 2026-10-10 23:10-23:25 | phase-1 | perf-battery | planning
Decided to run the performance battery from the Mac on a phone hotspot rather
than a dedicated cloud worker (a small EC2 instance in a separate VPC). The
hotspot has been reliable in practice, and setup cost and time favour it.
This is a threat to validity: a cellular access network adds latency and
throughput variance that is not caused by the access path under test.
Mitigations:
- record a control measurement (`ping -c 30 1.1.1.1`) before each path's run
  and journal it with the run ID, so anomalous runs can be flagged
- keep the location, device and time of day consistent, and note carrier and
  signal
- use repeated reps (5 per path) and report mean and standard deviation
- treat the cross-phase comparisons (vpn vs openziti vs netbird, all on the
  same hotspot) as the primary result; the home-LAN baseline differs in more
  than the access path

Ran the following commands:
```
# merge as usual (re-sign, fast-forward, push, delete branch), then:
cd node-reset
ansible-playbook -i inventory.yaml reset.yaml -l tpi2-3                        # back to the clean golden state

cd ../ansible-workloads
ansible-playbook -i inventory.yaml --vault-password-file ../.vault-pass site.yaml   # adds iperf3; existing grants unchanged

cd ../node-reset                                                               # recapture so resets keep iperf3
ansible-playbook -i inventory.yaml reset.yaml -l tpi2-3 --tags to-recovery
./capture-golden.sh tpi2-3 10.0.0.73
ansible-playbook -i inventory.yaml reset.yaml -l tpi2-3 --tags to-main,verify
```

The new golden checksum is `0008e8f5e4e9a838503b2603da2e30a4300942ec308f81acad6f16584b356533  rootfs.img.zst`, which now includes `iperf3` as part of the golden image.

```
$ route -n get 10.0.0.73 | grep interface
  interface: en0
$ iperf3 -c 10.0.0.73 -t 2
Connecting to host 10.0.0.73, port 5201
[  4] local 10.0.0.143 port 49787 connected to 10.0.0.73 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  4]   0.00-1.01   sec  12.0 MBytes   100 Mbits/sec  1231    260 KBytes       
[  4]   1.01-2.00   sec  11.1 MBytes  93.5 Mbits/sec   85    205 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  4]   0.00-2.00   sec  23.1 MBytes  96.8 Mbits/sec  1316            sender
[  4]   0.00-1.85   sec  22.9 MBytes   103 Mbits/sec                  receiver

iperf Done.
```

Control running over VPN
```
$ ping -c 30 1.1.1.1 | tail -1
round-trip min/avg/max/stddev = 29.644/36.930/60.168/6.520 ms
$ ./run_perf.py --phase phase-1 --path vpn --iperf-server 10.0.0.73 --http-url http://10.0.0.73:8080/
rep 1 throughput_up: 7.57 Mbps 
rep 1 throughput_down: 23.69 Mbps 
rep 1 http latency p50=146.1ms n=50
rep 2 throughput_up: 7.35 Mbps 
rep 2 throughput_down: 33.54 Mbps 
rep 2 http latency p50=1135.1ms n=50
rep 3 throughput_up: 0.29 Mbps 
rep 3 throughput_down: 14.68 Mbps 
rep 3 http latency p50=136.9ms n=50
rep 4 throughput_up: 9.95 Mbps 
rep 4 throughput_down: 29.04 Mbps 
rep 4 http latency p50=128.5ms n=50
rep 5 throughput_up: 7.91 Mbps 
rep 5 throughput_down: 29.04 Mbps 
rep 5 http latency p50=176.5ms n=50

25 rows -> results/phase-1_vpn_20261011T061620Z_8c4335212d4d.csv
```

AWS app running over VPN
```
$ ./run_perf.py --phase phase-1 --path vpn-aws --http-url http://10.100.10.10:8080/
rep 1 http latency p50=231.2ms n=50
rep 2 http latency p50=285.3ms n=50
rep 3 http latency p50=280.2ms n=50
rep 4 http latency p50=264.7ms n=50
rep 5 http latency p50=216.0ms n=50

15 rows -> results/phase-1_vpn-aws_20261011T061852Z_89ea2adc52f3.csv
```

## 2026-10-10 23:25-23:30 | phase-1 | perf-battery | testing
Reviewed the Phase 1 performance results (runs `f926e0d5420b` baseline,
`8c4335212d4d` vpn, `89ea2adc52f3` vpn-aws) and decided NOT to re-run them,
because of time. They are kept as the Phase 1 measurements with the
following limitations, which the analysis must account for:

- Baseline was measured over Wi-Fi, not wired. HTTP p50 to a static page
  on the same subnet was 16-80 ms per rep (expected about 1-3 ms wired) and
  upload varied 43-120 Mbps. The baseline therefore includes Wi-Fi
  latency and variance and does not cleanly isolate substrate cost.
- vpn (hotspot, remote-admin) had two anomalous reps out of five: rep 2
  p50 1135 ms (others 128-177 ms) and rep 3 upload 0.29 Mbps (others
  7.4-10.0 Mbps). With them, p50 is 345 +/- 442 ms; without them, about
  150 ms p50, 8 Mbps up, 29 Mbps down. The control ping taken before the
  run was normal (avg 36.9 ms, sd 6.5 ms), so conditions changed during
  the run, which a single pre-run control cannot detect.
- Latency maxima cluster near 1.14 s (and one at 2.88 s) on both vpn and
  vpn-aws. This is the pattern of TCP SYN retransmission (1 s, then +2 s),
  since curl opens a new connection per sample, so the maxima mostly
  reflect packet loss on the hotspot/UDP tunnel path, not server response.
- vpn-aws (HTTP only) was comparatively stable: p50 255 +/- 31 ms.

Analysis rules adopted for this and later phases: report the median across
reps alongside mean and standard deviation; use p50 as the headline
latency metric; report reps 2 and 3 of the vpn run (and any later
anomalous reps) rather than silently dropping them; treat cross-phase
comparisons on the same hotspot as primary, and baseline-vs-path as
indicative only. Possible future improvement, not done: a per-rep control
ping and a target column in run_perf.py.
