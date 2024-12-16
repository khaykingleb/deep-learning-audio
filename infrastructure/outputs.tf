output "k3s_servers_ips" {
  value       = module.k3s.servers_ips
  description = "IP addresses of the K3s server nodes."
}

output "k3s_servers_private_key" {
  value       = module.k3s.servers_private_key
  description = "Private key for SSH access to the K3s server nodes."
  sensitive   = true
}

output "kube_api_server" {
  value       = module.k3s.kube_api_server
  description = "API server of the K3s cluster."
}

output "kubeconfig" {
  value       = module.k3s.kubeconfig
  description = "Kubeconfig in YAML format"
  sensitive   = true
}
