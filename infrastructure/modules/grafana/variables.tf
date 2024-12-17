variable "enable_monitoring" {
  description = "Enable Grafana Cloud monitoring."
  type        = bool
  default     = false
}

variable "grafana_cloud_stack_slug" {
  description = "Grafana Cloud stack slug."
  type        = string
}

variable "grafana_cloud_access_policy_token" {
  description = "Grafana Cloud access policy token."
  type        = string
}
