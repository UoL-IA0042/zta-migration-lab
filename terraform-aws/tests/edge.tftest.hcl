mock_provider "aws" {
  mock_data "aws_ami" { defaults = { id = "ami-12345678" } }
  mock_data "aws_iam_policy_document" { defaults = { json = "{\"Version\":\"2012-10-17\",\"Statement\":[]}" } }
  mock_resource "aws_iam_policy" { defaults = { arn = "arn:aws:iam::123456789012:policy/mock" } }
  mock_resource "aws_iam_user" { defaults = { arn = "arn:aws:iam::123456789012:user/mock" } }
  mock_resource "aws_s3_bucket" { defaults = { arn = "arn:aws:s3:::mock-bucket" } }
}
mock_provider "random" {}

variables {
  ssh_key_name    = "test-key"
  lab_egress_cidr = "192.0.2.10/32"
}

run "phase1_no_edge" {
  command = plan
  assert {
    condition     = length(aws_instance.edge) == 0 && length(aws_security_group.edge) == 0 && length(aws_eip.edge) == 0
    error_message = "no edge host without an experiment flag"
  }
  assert {
    condition     = length([for i in aws_security_group.vpn_gateway.ingress : i if i.from_port == 8080]) == 0
    error_message = "hub must not admit the edge subnet without an experiment"
  }
}

run "openziti" {
  command = plan
  variables { enable_openziti = true }
  assert {
    condition     = length(aws_instance.edge) == 1
    error_message = "edge host for openziti"
  }
  assert {
    condition     = toset([for i in aws_security_group.edge[0].ingress : "${i.protocol}/${i.from_port}"]) == toset(["tcp/80", "tcp/443", "tcp/1280", "tcp/3022", "tcp/22"])
    error_message = "openziti ports"
  }
  assert {
    condition     = length([for i in aws_security_group.vpn_gateway.ingress : i if i.from_port == 8080 && contains(i.cidr_blocks, "10.100.1.0/24")]) == 1
    error_message = "hub admits the edge subnet on the Keycloak port"
  }
}

run "netbird" {
  command = plan
  variables { enable_netbird = true }
  assert {
    condition     = length(aws_instance.edge) == 1 && length(aws_eip.edge) == 1
    error_message = "edge host for netbird"
  }
  assert {
    condition     = toset([for i in aws_security_group.edge[0].ingress : "${i.protocol}/${i.from_port}"]) == toset(["tcp/80", "tcp/443", "udp/3478", "tcp/22"])
    error_message = "netbird ports (no openziti ports)"
  }
  assert {
    condition     = tolist([for i in aws_security_group.edge[0].ingress : i.cidr_blocks if i.from_port == 22][0]) == tolist(["192.0.2.10/32"])
    error_message = "ssh only from the lab egress address"
  }
  assert {
    condition     = length([for i in aws_security_group.vpn_gateway.ingress : i if i.from_port == 8080]) == 1
    error_message = "hub rule present for netbird"
  }
}

run "both_rejected" {
  command = plan
  variables {
    enable_openziti = true
    enable_netbird  = true
  }
  expect_failures = [aws_instance.edge]
}
