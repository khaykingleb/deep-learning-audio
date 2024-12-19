resource "null_resource" "k3s_installation_for_agents" {
  for_each = { for agent_name, agent_values in var.k3s_agents : agent_name => agent_values }

  depends_on = [
    null_resource.k3s_server_installation_for_main_node,
    null_resource.tailscale_activation_for_k3s_agents
  ]

  triggers = {
    k3s_version                  = var.k3s_version
    k3s_token                    = local.k3s_token
    k3s_main_server_private_ip   = local.k3s_main_server_private_ip
    k3s_server_private_key       = module.k3s_servers_key_pair.private_key_pem
    k3s_agent_node_name          = each.key
    k3s_agent_user               = each.value.user
    k3s_agent_public_ip          = each.value.host
    k3s_agent_private_key        = local.k3s_agents_private_keys[each.value.private_key_name]
    k3s_main_server_tailscale_ip = local.k3s_main_server_tailscale_ip
    tailscale_auth_key           = var.tailscale_auth_key
  }

  connection {
    type        = "ssh"
    user        = self.triggers.k3s_agent_user
    host        = self.triggers.k3s_agent_public_ip
    private_key = self.triggers.k3s_agent_private_key
  }

  provisioner "file" {
    when        = create
    destination = "/tmp/k3s_agent_install.sh"
    content = templatefile("${path.module}/scripts/k3s_agent_install.sh.tpl", {
      k3s_version                  = self.triggers.k3s_version,
      k3s_token                    = self.triggers.k3s_token,
      k3s_agent_node_name          = self.triggers.k3s_agent_node_name,
      k3s_main_server_tailscale_ip = self.triggers.k3s_main_server_tailscale_ip,
      tailscale_auth_key           = self.triggers.tailscale_auth_key,
    })
  }

  provisioner "remote-exec" {
    when = create
    inline = [
      "sudo hostnamectl set-hostname ${self.triggers.k3s_agent_node_name}",
      "sh /tmp/k3s_agent_install.sh"
    ]
  }

  provisioner "remote-exec" {
    when = destroy
    inline = [
      "/usr/local/bin/k3s-agent-uninstall.sh",
    ]
  }

  provisioner "remote-exec" {
    when = destroy
    # NOTE: this creates a connection to the k3s server, not the agent
    connection {
      type        = "ssh"
      user        = "ubuntu"
      host        = self.triggers.k3s_main_server_private_ip
      private_key = self.triggers.k3s_server_private_key
    }
    inline = [
      "sudo k3s kubectl delete node ${self.triggers.k3s_agent_node_name}",
    ]
  }
}
