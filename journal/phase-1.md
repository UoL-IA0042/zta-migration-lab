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