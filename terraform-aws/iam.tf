# Per-role IAM users. Policies encode the intended cloud access model
# probed by the test matrix (aws-s3-data read/write rows). Access keys
# are created out-of-band (aws iam create-access-key) and configured as
# AWS profiles named after the roles on the probing machines.

resource "aws_iam_user" "role_users" {
  for_each = toset(var.lab_roles)
  name     = each.key
  tags     = { Purpose = "access-matrix-probe" }
}

data "aws_iam_policy_document" "s3_read" {
  statement {
    actions   = ["s3:GetObject", "s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn, "${aws_s3_bucket.data.arn}/*"]
  }
}

data "aws_iam_policy_document" "s3_write" {
  statement {
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.data.arn}/*"]
  }
}

resource "aws_iam_policy" "s3_read" {
  name   = "zta-lab-s3-read"
  policy = data.aws_iam_policy_document.s3_read.json
}

resource "aws_iam_policy" "s3_write" {
  name   = "zta-lab-s3-write"
  policy = data.aws_iam_policy_document.s3_write.json
}

locals {
  # Matrix ground truth: admin read+write; developer and analyst read;
  # contractor nothing.
  read_roles  = ["remote-admin", "remote-developer", "remote-analyst"]
  write_roles = ["remote-admin"]
}

resource "aws_iam_user_policy_attachment" "read" {
  for_each   = toset(local.read_roles)
  user       = aws_iam_user.role_users[each.key].name
  policy_arn = aws_iam_policy.s3_read.arn
}

resource "aws_iam_user_policy_attachment" "write" {
  for_each   = toset(local.write_roles)
  user       = aws_iam_user.role_users[each.key].name
  policy_arn = aws_iam_policy.s3_write.arn
}
