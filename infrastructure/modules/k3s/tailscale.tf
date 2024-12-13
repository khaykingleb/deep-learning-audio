resource "tailscale_acl" "acl" {
  acl = templatefile("${path.module}/config/tailscale/acl.jsonc.tpl", {
    emails = var.tailscale_emails
  })
}

resource "null_resource" "tailscale_activation_for_k3s_servers" {
  for_each = { for server_idx, server_values in module.k3s_servers : server_idx => server_values }

  triggers = {
    tailscale_auth_key     = var.tailscale_auth_key
    k3s_server_ip          = each.value.public_ip
    k3s_server_private_key = module.k3s_servers_key_pair.private_key_pem
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    host        = self.triggers.k3s_server_ip
    private_key = self.triggers.k3s_server_private_key
  }

  provisioner "file" {
    when        = create
    destination = "/tmp/tailscale_activate.sh"
    content = templatefile("${path.module}/scripts/tailscale_activate.sh.tpl", {
      tailscale_auth_key = self.triggers.tailscale_auth_key
    })
  }

  provisioner "remote-exec" {
    when = create
    inline = [
      "sh /tmp/tailscale_activate.sh"
    ]
  }

  provisioner "remote-exec" {
    when = destroy
    inline = [
      "sudo tailscale logout",
      "sudo rm -f /usr/local/share/tailscale_ip.txt",
      "sudo apt-get purge tailscale -y",
      "sudo apt-get autoremove -y",
    ]
  }
}

data "remote_file" "tailscale_k3s_main_server_ip" {
  depends_on = [
    null_resource.tailscale_activation_for_k3s_servers
  ]

  conn {
    user        = "ubuntu"
    host        = local.k3s_server_main_ip
    private_key = module.k3s_servers_key_pair.private_key_pem
    sudo        = true
    timeout     = 10000
  }

  path = "/usr/local/share/tailscale_ip.txt"
}

data "remote_file" "tailscale_k3s_additional_servers_ips" {
  for_each = { for server_idx, server_values in module.k3s_servers : server_idx => server_values if server_idx != 0 }

  depends_on = [
    null_resource.tailscale_activation_for_k3s_servers
  ]

  conn {
    user        = "ubuntu"
    host        = each.value.public_ip
    private_key = module.k3s_servers_key_pair.private_key_pem
    sudo        = true
    timeout     = 10000
  }

  path = "/usr/local/share/tailscale_ip.txt"
}

resource "null_resource" "tailscale_activation_for_k3s_agents" {
  for_each = { for agent_name, agent_values in var.k3s_agents : agent_name => agent_values }

  triggers = {
    k3s_agent_user        = each.value.user
    k3s_agent_host        = each.value.host
    k3s_agent_private_key = local.k3s_agents_private_keys[each.value.private_key_name]
    tailscale_auth_key    = var.tailscale_auth_key
  }

  connection {
    type        = "ssh"
    user        = self.triggers.k3s_agent_user
    host        = self.triggers.k3s_agent_host
    private_key = self.triggers.k3s_agent_private_key
  }

  provisioner "file" {
    when        = create
    destination = "/tmp/tailscale_activate.sh"
    content = templatefile("${path.module}/scripts/tailscale_activate.sh.tpl", {
      tailscale_auth_key = self.triggers.tailscale_auth_key
    })
  }

  provisioner "remote-exec" {
    when = create
    inline = [
      "sh /tmp/tailscale_activate.sh"
    ]
  }

  provisioner "remote-exec" {
    when = destroy
    inline = [
      "sudo tailscale logout",
      "sudo rm /usr/local/share/tailscale_ip.txt",
      "sudo apt-get purge tailscale -y",
      "sudo apt-get autoremove -y",
    ]
  }
}

data "remote_file" "tailscale_k3s_agents_ips" {
  for_each = { for agent_name, agent_values in var.k3s_agents : agent_name => agent_values }

  depends_on = [
    null_resource.tailscale_activation_for_k3s_agents
  ]

  conn {
    user        = each.value.user
    host        = each.value.host
    private_key = local.k3s_agents_private_keys[each.value.private_key_name]
  }

  path = "/usr/local/share/tailscale_ip.txt"
}
