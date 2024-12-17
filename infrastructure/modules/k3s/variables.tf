variable "aws_region" {
  description = "AWS region to deploy the K3s servers in."
  type        = string
  default     = "us-east-1"
}

variable "tailscale_auth_key" {
  description = "Reusable and ephemeral Tailscale auth key to build a mesh via Tailscale VPN in the K3s cluster. Needs to have the tag `k3s-cluster`."
  type        = string
  sensitive   = true
}

variable "k3s_version" {
  description = "Version of K3s to install on the nodes. See https://github.com/k3s-io/k3s/releases for available versions."
  type        = string
}

variable "k3s_servers_count" {
  description = "Number of K3s servers to deploy to the cluster."
  type        = number
  default     = 1
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
