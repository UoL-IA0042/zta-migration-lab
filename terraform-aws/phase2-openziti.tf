# Phase 2 (OpenZiti): AWS edge host for the public ZTNA components.
# docs/phase-2-openziti.md. Kept in its own file and behind
# enable_openziti so the phase-1 tag stays reproducible and the phase
# diff stays legible.
#
# The edge host carries the OpenZiti controller (:1280), the public edge
# router (:3022) and the IdP reverse proxy (:80/:443, Let's Encrypt). Its
# Elastic IP gives the sslip.io names (idp/ctrl/router.<ip-dashed>.sslip.io).
# The lab only dials out to it; the IdP proxy reaches Keycloak through the
# Phase 1 site-to-site tunnel (edge subnet -> hub -> tpi2-4 -> 10.0.0.72).

variable "enable_openziti" {
  description = "Create the Phase 2 OpenZiti edge host (subnet, route table, security group, instance, Elastic IP)"
  type        = bool
  default     = false
}

variable "ziti_edge_instance_type" {
  description = "Edge host instance type (Graviton: controller + public router + proxy)"
  type        = string
  default     = "t4g.small"
}

variable "lab_idp_port" {
  description = "Keycloak HTTP port on tpi2-2, reached by the IdP proxy through the tunnel"
  type        = number
  default     = 8080
}

locals {
  # 10.100.1.0/24; also referenced by the hub security group (main.tf)
  edge_subnet_cidr = cidrsubnet(var.vpc_cidr, 8, 1)
  # Reachable by anyone: remote workers have no fixed address. The exposure
  # moves from the home gateway to the cloud and is authenticated-only.
  ziti_edge_public_ports = {
    "ACME HTTP-01 for the IdP certificate" = 80
    "IdP reverse proxy (HTTPS)"            = 443
    "OpenZiti controller client API"       = 1280
    "OpenZiti public edge router"          = 3022
  }
}

# Own subnet and route table: the public route table uses inline routes,
# which cannot be mixed with separate route resources.
resource "aws_subnet" "edge" {
  count                   = var.enable_openziti ? 1 : 0
  vpc_id                  = aws_vpc.lab.id
  cidr_block              = local.edge_subnet_cidr
  map_public_ip_on_launch = true
  tags                    = { Name = "zta-lab-edge" }
}

resource "aws_route_table" "edge" {
  count  = var.enable_openziti ? 1 : 0
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
  count          = var.enable_openziti ? 1 : 0
  subnet_id      = aws_subnet.edge[0].id
  route_table_id = aws_route_table.edge[0].id
}

resource "aws_security_group" "ziti_edge" {
  count  = var.enable_openziti ? 1 : 0
  name   = "zta-lab-ziti-edge"
  vpc_id = aws_vpc.lab.id

  dynamic "ingress" {
    for_each = local.ziti_edge_public_ports
    content {
      description = ingress.key
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
  ingress {
    description = "SSH from the lab (ansible-openziti configures this host)"
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

resource "aws_instance" "ziti_edge" {
  count                  = var.enable_openziti ? 1 : 0
  ami                    = data.aws_ami.ubuntu_arm64.id
  instance_type          = var.ziti_edge_instance_type
  subnet_id              = aws_subnet.edge[0].id
  key_name               = var.ssh_key_name
  vpc_security_group_ids = [aws_security_group.ziti_edge[0].id]
  tags                   = { Name = "zta-lab-ziti-edge" }
  # Controller, public router and IdP proxy are configured by
  # ansible-openziti against this host.
}

# Stable address: the sslip.io names, the Keycloak issuer and the
# enrolled identities all embed it.
resource "aws_eip" "ziti_edge" {
  count      = var.enable_openziti ? 1 : 0
  instance   = aws_instance.ziti_edge[0].id
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]
  tags       = { Name = "zta-lab-ziti-edge" }
}

output "edge_host_public_ip" {
  description = "Elastic IP of the Phase 2 edge host (export as LAB_EDGE_IP); null unless enable_openziti"
  value       = try(aws_eip.ziti_edge[0].public_ip, null)
}
