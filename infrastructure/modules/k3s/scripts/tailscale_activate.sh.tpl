#!/bin/bash
set -e

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Connect node to the Tailscale network to get a Tailscale IP
sudo tailscale up --auth-key="${tailscale_auth_key}"

# Save the Tailscale IP to a temporary file
sudo tailscale ip -4 | sudo tee /usr/local/share/tailscale_ip.txt
