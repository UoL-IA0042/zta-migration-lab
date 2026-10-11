# Phase 2: AWS edge host for the public ZTNA components of whichever
# experiment is enabled (docs/phase-2-openziti.md, docs/phase-2-netbird.md).
# Kept in its own file and behind the experiment flags so the phase-1 tag
# stays reproducible and each phase diff stays legible. One experiment at
# a time: both run from the same Phase 1 baseline.
#
#   enable_openziti: controller (:1280), public edge router (:3022)
#   enable_netbird:  management server, signal and relay (behind :443),
#                    STUN (:3478/udp)
#   both:            IdP reverse proxy (:80/:443, Let's Encrypt)
#
# The Elastic IP gives the sslip.io names (<name>.<ip-dashed>.sslip.io).
# The lab only dials out to it; the IdP proxy reaches Keycloak through the
# Phase 1 site-to-site tunnel (edge subnet -> hub -> tpi2-4 -> 10.0.0.72).

# Inputs (enable_openziti, enable_netbird, edge_instance_type,
# lab_idp_port) are in variables.tf with the rest.

locals {
  edge_enabled = var.enable_openziti || var.enable_netbird
  # 10.100.1.0/24; also referenced by the hub security group (main.tf)
  edge_subnet_cidr = cidrsubnet(var.vpc_cidr, 8, 1)
  # Reachable by anyone: remote workers have no fixed address. The exposure
  # moves from the home gateway to the cloud and is authenticated-only.
  edge_public_tcp_ports = merge(
    {
      "ACME HTTP-01 for the TLS certificates" = 80
      "Reverse proxy (HTTPS)"                 = 443
    },
    var.enable_openziti ? {
      "OpenZiti controller client API" = 1280
      "OpenZiti public edge router"    = 3022
    } : {},
  )
  edge_public_udp_ports = var.enable_netbird ? {
    "NetBird STUN" = 3478
  } : {}
}

# Own subnet and route table: the public route table uses inline routes,
# which cannot be mixed with separate route resources.
resource "aws_subnet" "edge" {
  count                   = local.edge_enabled ? 1 : 0
  vpc_id                  = aws_vpc.lab.id
  cidr_block              = local.edge_subnet_cidr
  map_public_ip_on_launch = true
  tags                    = { Name = "zta-lab-edge" }
}

resource "aws_route_table" "edge" {
  count  = local.edge_enabled ? 1 : 0
  vpc_id = aws_vpc.lab.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  # IdP proxy -> Keycloak on the lab LAN, through the site-to-site hub
  route {
    cidr_block           = var.onprem_cidr
    network_interface_id = aws_instance.vpn_gateway.primary_network_interface_id
  }
  tags = { Name = "zta-lab-edge" }
}

resource "aws_route_table_association" "edge" {
  count          = local.edge_enabled ? 1 : 0
  subnet_id      = aws_subnet.edge[0].id
  route_table_id = aws_route_table.edge[0].id
}

resource "aws_security_group" "edge" {
  count  = local.edge_enabled ? 1 : 0
  name   = "zta-lab-edge"
  vpc_id = aws_vpc.lab.id

  dynamic "ingress" {
    for_each = local.edge_public_tcp_ports
    content {
      description = ingress.key
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
  dynamic "ingress" {
    for_each = local.edge_public_udp_ports
    content {
      description = ingress.key
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "udp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
  ingress {
    description = "SSH from the lab (Ansible configures this host)"
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

resource "aws_instance" "edge" {
  count                  = local.edge_enabled ? 1 : 0
  ami                    = data.aws_ami.ubuntu_arm64.id
  instance_type          = var.edge_instance_type
  subnet_id              = aws_subnet.edge[0].id
  key_name               = var.ssh_key_name
  vpc_security_group_ids = [aws_security_group.edge[0].id]
  tags                   = { Name = "zta-lab-edge" }
  # Configured by ansible-openziti or ansible-netbird against this host.

  lifecycle {
    precondition {
      condition     = !(var.enable_openziti && var.enable_netbird)
      error_message = "Enable one experiment at a time: enable_openziti or enable_netbird, not both."
    }
  }
}

# Stable address: the sslip.io names and the Keycloak issuer embed it.
resource "aws_eip" "edge" {
  count      = local.edge_enabled ? 1 : 0
  instance   = aws_instance.edge[0].id
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]
  tags       = { Name = "zta-lab-edge" }
}

output "edge_host_public_ip" {
  description = "Elastic IP of the Phase 2 edge host (export as LAB_EDGE_IP); null unless an experiment flag is set"
  value       = try(aws_eip.edge[0].public_ip, null)
}
