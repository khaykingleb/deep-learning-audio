

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.26.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "4.0.1"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.2.3"
    }
  }
}

provider "aws" {
  region = var.region
}

provider "tls" {}

provider "local" {}
