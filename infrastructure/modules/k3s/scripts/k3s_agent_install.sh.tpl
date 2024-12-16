#!/bin/bash
set -e

# Get the Tailscale IP address
k3s_agent_tailscale_ip=$(tailscale ip -4)

# Install K3s agent and join it to the cluster using Tailscale network
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="${k3s_version}" K3S_TOKEN="${k3s_token}" sh -s - agent \
    --node-name "${k3s_agent_node_name}" \
    --server "https://${k3s_main_server_tailscale_ip}:6443" \
    --vpn-auth "name=tailscale,joinKey=${tailscale_auth_key}" \
    --node-external-ip "$k3s_agent_tailscale_ip"
