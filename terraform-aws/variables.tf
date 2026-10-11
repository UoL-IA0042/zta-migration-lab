variable "aws_region" {
  description = "Single region for all lab resources (performance repeatability)"
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "Lab VPC CIDR (must match docs/addressing.md)"
  type        = string
  default     = "10.100.0.0/16"
}

variable "onprem_cidr" {
  description = "On-premises lab network, reached via the VPN tunnel"
  type        = string
  default     = "10.0.0.0/24"
}

variable "lab_egress_cidr" {
  description = "The lab's public egress address as a /32 (site-to-site and SSH ingress to the VPN gateway). Supply via -var or terraform.tfvars; never commit it."
  type        = string

  validation {
    condition     = can(cidrhost(var.lab_egress_cidr, 0)) && endswith(var.lab_egress_cidr, "/32")
    error_message = "Use a single address in CIDR form, e.g. 203.0.113.7/32."
  }
}

variable "vpn_client_cidr" {
  description = "OpenVPN client subnet (phase 1)"
  type        = string
  default     = "10.9.0.0/24"
}

variable "app_private_ip" {
  description = "Fixed private IP for the workload app (matrix: aws-app)"
  type        = string
  default     = "10.100.10.10"
}

variable "data_bucket_name" {
  description = "S3 data bucket name prefix (matrix: aws-s3-data); a random 6-character suffix is appended for global uniqueness"
  type        = string
  default     = "lab-data-bucket"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,48}[a-z0-9]$", var.data_bucket_name))
    error_message = "Use 3-50 lowercase letters, digits or hyphens; the suffix brings the name to at most 57 of S3's 63 characters."
  }
}

variable "instance_type" {
  description = "Graviton (ARM64) instance type for architectural parity with the RK1 nodes"
  type        = string
  default     = "t4g.micro"
}

variable "ssh_key_name" {
  description = "Existing EC2 key pair name for instance access"
  type        = string
}

# Roles must match OpenVPN clients, Keycloak realm roles, and the test matrix.
variable "lab_roles" {
  description = "Experimental role identities"
  type        = list(string)
  default     = ["remote-admin", "remote-developer", "remote-analyst", "remote-contractor"]
}

# Phase 2 experiments, used by phase2-edge.tf and the hub security
# group in main.tf. docs/phase-2-openziti.md, docs/phase-2-netbird.md.
variable "enable_openziti" {
  description = "Phase 2 OpenZiti experiment: create the edge host (subnet, route table, security group, instance, Elastic IP) with the OpenZiti ports"
  type        = bool
  default     = false
}

variable "enable_netbird" {
  description = "Phase 2 NetBird experiment: create the edge host with the NetBird ports (STUN 3478/udp); not together with enable_openziti"
  type        = bool
  default     = false
}

variable "edge_instance_type" {
  description = "Edge host instance type (Graviton: the experiment's public components + IdP proxy)"
  type        = string
  default     = "t4g.small"
}

variable "lab_idp_port" {
  description = "Keycloak HTTP port on tpi2-2, reached by the IdP proxy through the tunnel"
  type        = number
  default     = 8080
}
