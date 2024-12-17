resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }
}

# https://github.com/grafana/k8s-monitoring-helm/tree/main/charts/k8s-monitoring
resource "helm_release" "k8s_monitoring" {
  count = var.enable_monitoring ? 1 : 0

  repository = "https://grafana.github.io/helm-charts"
  chart      = "k8s-monitoring"
  # NB: be careful about the metrics cardinality when bumping the version
  # The metrics cardinality should be as low as possible to pay the free costs for monitoring
  version = "~> 1.6.13"

  name      = "k8s-monitoring"
  namespace = kubernetes_namespace.monitoring.metadata[0].name

  values = [
    templatefile("${path.module}/config/k8s_monitoring.yaml.tpl", {
      cluster_name                = "dori"
      grafana_access_policy_token = var.grafana_access_policy_token
      grafana_prometheus_host     = var.grafana_prometheus_host
      grafana_prometheus_username = var.grafana_prometheus_username
      grafana_loki_host           = var.grafana_loki_host
      grafana_loki_username       = var.grafana_loki_username
    })
  ]
}
