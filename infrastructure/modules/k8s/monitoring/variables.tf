variable "enable_monitoring" {
  description = "Enable monitoring."
  type        = bool
  default     = false
}

variable "grafana_access_policy_token" {
  description = "Grafana access policy token."
  type        = string
  sensitive   = true
}

variable "grafana_prometheus_host" {
  description = "Prometheus host."
  type        = string

  validation {
    condition     = can(regex(".*/api/prom/push$", var.grafana_prometheus_host)) ? false : true
    error_message = "The Prometheus host must not end with /api/prom/push."
  }
}

variable "grafana_prometheus_username" {
  description = "Prometheus username."
  type        = string
}

variable "grafana_loki_host" {
  description = "Loki host."
  type        = string

  validation {
    condition     = can(regex(".*/api/v1/push$", var.grafana_loki_host)) ? false : true
    error_message = "The Loki host must not end with /api/v1/push."
  }
}

variable "grafana_loki_username" {
  description = "Loki username."
  type        = string
}
