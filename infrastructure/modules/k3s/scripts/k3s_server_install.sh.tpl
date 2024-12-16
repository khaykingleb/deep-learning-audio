#!/bin/bash
set -e

# Get the Tailscale IP address
k3s_server_tailscale_ip=$(tailscale ip -4)

# Install K3s server and join it to the cluster using Tailscale network
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="${k3s_version}" K3S_TOKEN="${k3s_token}" sh -s - server \
    %{if is_main_node == true} \
    --cluster-init \
    %{else} \
    --server "https://${k3s_main_server_private_ip}:6443" \
    %{endif} \
    --node-ip "${k3s_server_private_ip}" \
    --tls-san "${k3s_server_public_ip}" \
    --vpn-auth "name=tailscale,joinKey=${tailscale_auth_key}" \
    --node-external-ip "$k3s_server_tailscale_ip" \
    --tls-san "$k3s_server_tailscale_ip"
