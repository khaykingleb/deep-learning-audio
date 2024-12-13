resource "grafana_folder" "general" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.stack

  title = "Root"
}

resource "grafana_dashboard" "gpu" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.stack

  folder      = grafana_folder.general[0].id
  config_json = file("${path.module}/config/dashboards/root/gpu.json")
}

resource "grafana_folder" "kubernetes" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.stack

  title = "Kubernetes"
}

resource "grafana_dashboard" "k8s_global" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.stack

  folder      = grafana_folder.kubernetes[0].id
  config_json = file("${path.module}/config/dashboards/k8s/global.json")
}

resource "grafana_dashboard" "k8s_namespaces" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.stack

  folder      = grafana_folder.kubernetes[0].id
  config_json = file("${path.module}/config/dashboards/k8s/namespaces.json")
}

resource "grafana_dashboard" "k8s_nodes" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.stack

  folder      = grafana_folder.kubernetes[0].id
  config_json = file("${path.module}/config/dashboards/k8s/nodes.json")
}

resource "grafana_dashboard" "k8s_pods" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.stack

  folder      = grafana_folder.kubernetes[0].id
  config_json = file("${path.module}/config/dashboards/k8s/pods.json")
}
