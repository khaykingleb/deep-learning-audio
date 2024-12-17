output "servers_ips" {
  value       = module.k3s_servers[*].public_ip
  description = "IP addresses of the K3s server nodes."
}

output "servers_private_key" {
  value       = module.k3s_servers_key_pair.private_key_pem
  description = "Private key for SSH access to the K3s server nodes."
  sensitive   = true
}

output "kubeconfig" {
  value       = local.kubeconfig
  description = "Kubeconfig file for the K3s cluster."
  sensitive   = true
}

output "kube_api_server" {
  value       = local.kube_api_server
  description = "Kube API server for the K3s cluster."
}

output "kube_client_certificate" {
  value       = local.kube_client_certificate
  description = "Client certificate for the K3s cluster."
  sensitive   = true
}

output "kube_client_key" {
  value       = local.kube_client_key
  description = "Client key for the K3s cluster."
  sensitive   = true
}

output "kube_cluster_ca_certificate" {
  value       = local.kube_cluster_ca_certificate
  description = "Cluster CA certificate for the K3s cluster."
  sensitive   = true
}
