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
  description = "S3 data bucket (matrix: aws-s3-data); bucket names are global, override with a unique suffix"
  type        = string
  default     = "lab-data-bucket"
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
