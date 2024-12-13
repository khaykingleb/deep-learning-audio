locals {
  us_east_1_ubuntu_22_04_x86_ami = "ami-0fc5d935ebf8bc3bc"

  k3s_server_main_ip = module.k3s_servers[0].public_ip
  k3s_token          = sensitive(trimspace(data.remote_file.k3s_server_token.content))

  tailscale_k3s_main_server_ip         = trimspace(data.remote_file.tailscale_k3s_main_server_ip.content)
  tailscale_k3s_additional_servers_ips = { for server_idx, node_values in data.remote_file.tailscale_k3s_additional_servers_ips : server_idx => trimspace(node_values.content) }
  tailscale_k3s_agents_ips             = { for agent_name, node_values in data.remote_file.tailscale_k3s_agents_ips : agent_name => trimspace(node_values.content) }

  kube_api_server             = "https://${local.k3s_server_main_ip}:6443"
  kubeconfig                  = replace(data.remote_file.kubeconfig.content, "https://127.0.0.1:6443", local.kube_api_server)
  kube_client_certificate     = sensitive(base64decode(yamldecode(local.kubeconfig).users[0].user.client-certificate-data))
  kube_client_key             = sensitive(base64decode(yamldecode(local.kubeconfig).users[0].user.client-key-data))
  kube_cluster_ca_certificate = sensitive(base64decode(yamldecode(local.kubeconfig).clusters[0].cluster.certificate-authority-data))

  k3s_agents_private_keys = {
    "shadeform" = var.shadeform_private_key
  }
}

data "remote_file" "kubeconfig" {
  depends_on = [
    null_resource.k3s_server_installation_for_main_node
  ]

  conn {
    sudo        = true
    user        = "ubuntu"
    host        = local.k3s_server_main_ip
    private_key = module.k3s_servers_key_pair.private_key_pem
    timeout     = 10000
  }

  path = "/etc/rancher/k3s/k3s.yaml"
}
