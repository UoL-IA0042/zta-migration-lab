terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project = "zta-migration-lab"
      Managed = "terraform"
    }
  }
}

# --- Network ----------------------------------------------------------

resource "aws_vpc" "lab" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "zta-lab" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.lab.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 0) # 10.100.0.0/24
  map_public_ip_on_launch = true
  tags                    = { Name = "zta-lab-public" }
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.lab.id
  cidr_block = cidrsubnet(var.vpc_cidr, 8, 10) # 10.100.10.0/24
  tags       = { Name = "zta-lab-private" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.lab.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.lab.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Private subnet routes on-prem + VPN client traffic via the VPN gateway
# instance (phase 1 site-to-site terminates there).
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.lab.id
  route {
    cidr_block           = var.onprem_cidr
    network_interface_id = aws_instance.vpn_gateway.primary_network_interface_id
  }
  route {
    cidr_block           = var.vpn_client_cidr
    network_interface_id = aws_instance.vpn_gateway.primary_network_interface_id
  }
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# --- Security groups --------------------------------------------------

resource "aws_security_group" "vpn_gateway" {
  name   = "zta-lab-vpn-gateway"
  vpc_id = aws_vpc.lab.id

  ingress {
    description = "OpenVPN site-to-site from the public address of the lab"
    from_port   = 1194
    to_port     = 1194
    protocol    = "udp"
    cidr_blocks = [var.lab_egress_cidr]
  }
  ingress {
    description = "SSH from the lab (ansible-openvpn configures this host)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.lab_egress_cidr]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Phase 1 posture: workloads trust anything arriving through the tunnel.
# This deliberate over-breadth is part of the perimeter baseline.
resource "aws_security_group" "workload" {
  name   = "zta-lab-workload"
  vpc_id = aws_vpc.lab.id

  ingress {
    description = "All traffic from on-prem and VPN clients via tunnel"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.onprem_cidr, var.vpn_client_cidr, var.vpc_cidr]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Instances (Graviton/ARM64 for parity with RK1) -------------------

data "aws_ami" "ubuntu_arm64" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-arm64-server-*"]
  }
}

resource "aws_instance" "vpn_gateway" {
  ami                    = data.aws_ami.ubuntu_arm64.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  key_name               = var.ssh_key_name
  vpc_security_group_ids = [aws_security_group.vpn_gateway.id]
  source_dest_check      = false # routes tunnel traffic
  tags                   = { Name = "zta-lab-vpn-gateway" }
  # OpenVPN site-to-site hub config is applied by ansible-openvpn
  # against this host (see that component's README).
}

# Stable public address for the hub: tpi2-4's site-to-site profile embeds
# it, so it must survive instance stop/start.
resource "aws_eip" "vpn_gateway" {
  instance   = aws_instance.vpn_gateway.id
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]
  tags       = { Name = "zta-lab-vpn-gateway" }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu_arm64.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.private.id
  private_ip             = var.app_private_ip
  key_name               = var.ssh_key_name
  vpc_security_group_ids = [aws_security_group.workload.id]
  tags                   = { Name = "zta-lab-app" }

  # The private subnet has no route to the internet, so nothing can be
  # installed at boot; serve the page with the AMI's python3 instead.
  user_data_replace_on_change = true
  user_data                   = <<-EOF
    #!/bin/bash
    set -euo pipefail
    mkdir -p /srv/lab-app
    echo '<h1>AWS lab application</h1>' > /srv/lab-app/index.html
    cat > /etc/systemd/system/lab-app.service <<'UNIT'
    [Unit]
    Description=AWS lab application (matrix: aws-app)
    After=network-online.target
    Wants=network-online.target
    [Service]
    ExecStart=/usr/bin/python3 -m http.server 8080 --directory /srv/lab-app
    DynamicUser=yes
    Restart=always
    [Install]
    WantedBy=multi-user.target
    UNIT
    systemctl daemon-reload
    systemctl enable --now lab-app.service
  EOF
}

# --- S3 data bucket (matrix: aws-s3-data) -----------------------------

# Bucket names are global. The suffix is generated once per environment
# and stays stable across applies; a destroy/rebuild yields a new one,
# so consumers read the name from `terraform output data_bucket`.
resource "random_string" "bucket_suffix" {
  length  = 6
  special = false
  upper   = false # S3 bucket names must be lowercase
}

locals {
  data_bucket_name = "${var.data_bucket_name}-${random_string.bucket_suffix.result}"
}

resource "aws_s3_bucket" "data" {
  bucket = local.data_bucket_name
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "probe_seed" {
  bucket  = aws_s3_bucket.data.id
  key     = "probe.txt"
  content = "seed object for access-matrix read probes\n"
}
