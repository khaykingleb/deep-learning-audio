locals {
  full_project_name = "${var.environment}-${var.project_name}"
  tags = {
    owner        = "Gleb Khaykin"
    project_name = local.full_project_name
  }
}

####################################################################################################
# S3
####################################################################################################

resource "aws_s3_bucket" "this" {
  bucket = "${local.full_project_name}-bucket"
  tags   = merge({ name = "DLA-S3-Bucket" }, local.tags)
}

resource "aws_s3_bucket_acl" "this" {
  bucket = aws_s3_bucket.this.id
  acl    = "private"
}

resource "aws_iam_user_policy" "s3" {
  name = "dla-s3-policy"
  user = "dla-user"

  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": "*"
        }
    ]
  }
  EOF
}

####################################################################################################
# EC2
####################################################################################################
