locals {
  tags = {
    owner             = "Gleb Khaykin"
    full_project_name = "${var.environment}-${var.project_name}"
  }
}

####################################################################################################
# S3
####################################################################################################

resource "aws_s3_bucket" "this" {
  bucket = "${var.project_name}-bucket"
  tags   = merge({ name = "DLA-S3-Bucket" }, local.tags)
}

resource "aws_s3_bucket_acl" "this" {
  bucket = aws_s3_bucket.this.id
  acl    = "private"
}

####################################################################################################
# EC2
####################################################################################################
