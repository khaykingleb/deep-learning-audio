terraform {
  required_version = ">= 1.8.6"

  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "~> 3.15.0"
    }
  }
}

provider "grafana" {
  alias                     = "cloud"
  cloud_access_policy_token = var.grafana_cloud_access_policy_token
}

provider "grafana" {
  alias = "stack"

  url  = data.grafana_cloud_stack.this[0].url
  auth = grafana_cloud_stack_service_account_token.cloud_sa[0].key
}
