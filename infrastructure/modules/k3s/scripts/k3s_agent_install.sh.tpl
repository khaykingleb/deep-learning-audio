#!/bin/bash
set -e

curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="${k3s_version}" sh -s - agent \
    --node-name "${k3s_agent_node_name}" \
    --token "${k3s_token}" \
    --server "https://${tailscale_k3s_main_server_ip}:6443" \
    --vpn-auth "name=tailscale,joinKey=${tailscale_auth_key}" \
    --node-external-ip "${tailscale_k3s_agent_ip}"
