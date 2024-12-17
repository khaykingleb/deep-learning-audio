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
