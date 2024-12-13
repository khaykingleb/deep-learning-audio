terraform {
  required_version = ">= 1.8.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80.0"
    }
    tailscale = {
      source  = "tailscale/tailscale"
      version = "~> 0.17.2"
    }
    remote = {
      source  = "tenstad/remote"
      version = "~> 0.1.3"
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

provider "tailscale" {
  tailnet             = "tail7ec8c1.ts.net"
  oauth_client_id     = var.tailscale_oauth_id
  oauth_client_secret = var.tailscale_oauth_secret
}
