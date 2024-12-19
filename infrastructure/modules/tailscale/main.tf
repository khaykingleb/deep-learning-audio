resource "tailscale_acl" "acl" {
  acl = file("${path.module}/config/tailscale/acl.jsonc")
}

resource "tailscale_tailnet_key" "k3s_cluster" {
  depends_on = [
    tailscale_acl.acl
  ]

  description = "Auth key for Tailscale VPN in K3s cluster"

  reusable      = true
  ephemeral     = true
  preauthorized = true
  tags          = ["tag:k3s-cluster"]

  recreate_if_invalid = "always"
}
