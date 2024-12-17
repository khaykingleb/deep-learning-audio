terraform {
  required_version = ">= 1.8.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80.0"
    }
    remote = {
      source  = "tenstad/remote"
      version = "~> 0.1.3"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.3"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2.3"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
