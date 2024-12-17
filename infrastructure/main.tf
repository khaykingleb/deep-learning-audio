module "tailscale" {
  source = "./modules/tailscale"

  tailscale_oauth_id     = var.tailscale_oauth_id
  tailscale_oauth_secret = var.tailscale_oauth_secret
}

module "k3s" {
  source = "./modules/k3s"

  k3s_version       = var.k3s_version
  k3s_servers_count = var.k3s_servers_count
  k3s_agents        = var.k3s_agents

  tailscale_auth_key    = module.tailscale.k3s_cluster_auth_key
  shadeform_private_key = var.shadeform_private_key
}

module "grafana_cloud" {
  source = "./modules/grafana"

  enable_monitoring                 = var.enable_monitoring
  grafana_cloud_stack_slug          = var.grafana_cloud_stack_slug
  grafana_cloud_access_policy_token = var.grafana_cloud_access_policy_token
}

module "k8s_monitoring" {
  source = "./modules/k8s/monitoring"

  enable_monitoring           = var.enable_monitoring
  grafana_access_policy_token = module.grafana_cloud.alloy_access_token
  grafana_prometheus_host     = module.grafana_cloud.prometheus_url
  grafana_prometheus_username = module.grafana_cloud.prometheus_user_id
  grafana_loki_host           = module.grafana_cloud.loki_url
  grafana_loki_username       = module.grafana_cloud.loki_user_id
}
