output "vpn_gateway_public_ip" {
  description = "Public IP the on-prem OpenVPN peers with (site-to-site)"
  value       = aws_instance.vpn_gateway.public_ip
}

output "app_private_ip" {
  description = "Workload app address (matrix: aws-app)"
  value       = aws_instance.app.private_ip
}

output "data_bucket" {
  description = "S3 data bucket (matrix: aws-s3-data)"
  value       = aws_s3_bucket.data.id
}

output "role_user_arns" {
  description = "Per-role IAM users; create access keys out-of-band"
  value       = { for r, u in aws_iam_user.role_users : r => u.arn }
}
