output "k3s_cluster_auth_key" {
  value       = tailscale_tailnet_key.k3s_cluster.key
  description = "Auth key for Tailscale VPN in K3s cluster"
  sensitive   = true
}
