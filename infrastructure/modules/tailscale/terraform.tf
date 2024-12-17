terraform {
  required_version = ">= 1.8.6"

  required_providers {
    tailscale = {
      source  = "tailscale/tailscale"
      version = "~> 0.17.2"
    }
  }
}

provider "tailscale" {
  tailnet             = "tail7ec8c1.ts.net"
  oauth_client_id     = var.tailscale_oauth_id
  oauth_client_secret = var.tailscale_oauth_secret
}
