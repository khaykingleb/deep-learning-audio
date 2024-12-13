data "grafana_cloud_stack" "this" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.cloud

  slug = var.grafana_cloud_stack_slug
}

# Create a service account and key for the stack
resource "grafana_cloud_stack_service_account" "cloud_sa" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.cloud

  stack_slug  = data.grafana_cloud_stack.this[0].slug
  name        = "cloud service account"
  role        = "Admin"
  is_disabled = false
}

resource "grafana_cloud_stack_service_account_token" "cloud_sa" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.cloud

  stack_slug         = data.grafana_cloud_stack.this[0].slug
  name               = "terraform service account key"
  service_account_id = grafana_cloud_stack_service_account.cloud_sa[0].id
}

# Create an access policy for Grafana Alloy
resource "grafana_cloud_access_policy" "grafana_alloy" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.cloud

  region       = data.grafana_cloud_stack.this[0].region_slug
  name         = "grafana-alloy-access-policy"
  display_name = "Grafana Alloy Access Policy (created by Terraform)"

  scopes = [
    "metrics:write",
    "metrics:import",
    "logs:write",
    "traces:write",
    "alerts:write",
    "rules:write",
  ]

  realm {
    type       = "stack"
    identifier = data.grafana_cloud_stack.this[0].id
  }
}

resource "grafana_cloud_access_policy_token" "grafana_alloy" {
  count    = var.enable_monitoring ? 1 : 0
  provider = grafana.cloud

  region           = data.grafana_cloud_stack.this[0].region_slug
  access_policy_id = grafana_cloud_access_policy.grafana_alloy[0].policy_id
  name             = "grafana-alloy-access-token"
  display_name     = "Grafana Alloy Access Token (created by Terraform)"
}
