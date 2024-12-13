output "alloy_access_token" {
  description = "Grafana Alloy access token."
  value       = grafana_cloud_access_policy_token.grafana_alloy[0].token
  sensitive   = true
}

output "prometheus_url" {
  description = "Grafana Cloud prometheus URL."
  value       = data.grafana_cloud_stack.this[0].prometheus_url
}

output "prometheus_user_id" {
  description = "Grafana Cloud prometheus user ID."
  value       = data.grafana_cloud_stack.this[0].prometheus_user_id
}

output "loki_url" {
  description = "Grafana Cloud loki URL."
  value       = data.grafana_cloud_stack.this[0].logs_url
}

output "loki_user_id" {
  description = "Grafana Cloud loki user ID."
  value       = data.grafana_cloud_stack.this[0].logs_user_id
}
