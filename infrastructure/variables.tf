# Tailscale
variable "tailscale_oauth_id" {
  description = "Tailscale OAuth client ID."
  type        = string
  sensitive   = true
}

variable "tailscale_oauth_secret" {
  description = "Tailscale OAuth client secret."
  type        = string
  sensitive   = true
}

# K3s

variable "k3s_version" {
  description = "Version of K3s to install on the nodes. See https://github.com/k3s-io/k3s/releases for available versions."
  type        = string
}

variable "k3s_servers_count" {
  description = "Number of K3s servers to deploy to the cluster."
  type        = number
  default     = 1

  validation {
    condition     = var.k3s_servers_count % 2 == 1
    error_message = "The number of K3s servers must be an odd number."
  }
}

variable "k3s_agents" {
  description = "K3s agent nodes to deploy to the K3s cluster."
  type = map(object({
    host             = string
    user             = string
    private_key_name = string
    provider         = string
    labels           = optional(list(string), [])
    taints           = optional(list(string), [])
  }))
  default = {}
}

variable "shadeform_private_key" {
  description = "Private key for Shadeform."
  type        = string
  sensitive   = true
}

# Grafana Cloud

variable "enable_monitoring" {
  description = "Enable Grafana Cloud monitoring."
  type        = bool
  default     = false
}

variable "grafana_cloud_stack_slug" {
  description = "Grafana Cloud stack slug to use for monitoring."
  type        = string
}

variable "grafana_cloud_access_policy_token" {
  description = "Grafana Cloud access policy token."
  type        = string
  sensitive   = true
}
