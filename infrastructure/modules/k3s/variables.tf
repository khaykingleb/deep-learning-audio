variable "aws_region" {
  description = "The AWS region to deploy the AWS nodes in the K3s cluster."
  type        = string
  default     = "us-east-1"
}

variable "tailscale_oauth_id" {
  description = "The OAuth client ID."
  type        = string
  sensitive   = true
}

variable "tailscale_oauth_secret" {
  description = "The OAuth client secret."
  type        = string
  sensitive   = true
}

variable "tailscale_auth_key" {
  description = "The reusable auth key to build a mesh via Tailscale VPN in the K3s cluster."
  type        = string
  sensitive   = true
}

variable "tailscale_emails" {
  description = "The emails of the users to automatically approve routes for."
  type        = list(string)
}

variable "k3s_version" {
  description = "The version of k3s to install on the nodes. See https://github.com/k3s-io/k3s/releases for available versions."
  type        = string
}

variable "k3s_servers_count" {
  description = "The number of servers to deploy to the cluster."
  type        = number
  default     = 1
}

variable "k3s_agents" {
  description = "The agents to deploy to the cluster."
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
  description = "The private key for Shadeform."
  type        = string
  sensitive   = true
}
