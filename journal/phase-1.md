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
