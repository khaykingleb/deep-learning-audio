# https://github.com/terraform-aws-modules/terraform-aws-vpc
module "k3s_servers_vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.16.0"

  name            = "k3s-servers-vpc"
  cidr            = "10.0.0.0/16"
  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  public_subnets  = ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.100.0/24", "10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}

data "aws_availability_zones" "available" {}

# https://github.com/terraform-aws-modules/terraform-aws-security-group
module "k3s_servers_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.2.0"

  name   = "k3s-servers-sg"
  vpc_id = module.k3s_servers_vpc.vpc_id

  ingress_with_cidr_blocks = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "External SSH access to nodes."
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 6443
      to_port     = 6443
      protocol    = "tcp"
      description = "External kubectl access to nodes."
      cidr_blocks = "0.0.0.0/0"
    },
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      description = "Allow all outbound access."
      cidr_blocks = "0.0.0.0/0"
    },
  ]
}

# https://github.com/terraform-aws-modules/terraform-aws-key-pair
module "k3s_servers_key_pair" {
  source  = "terraform-aws-modules/key-pair/aws"
  version = "~> 2.0.3"

  key_name           = "k3s-servers"
  create_private_key = true
}

# https://github.com/terraform-aws-modules/terraform-aws-ec2-instance
module "k3s_servers" {
  count = var.k3s_servers_count

  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 5.7.1"

  name          = "k3s-server-${count.index}"
  instance_type = "t3.medium"
  ami           = local.us_east_1_ubuntu_22_04_x86_ami
  key_name      = module.k3s_servers_key_pair.key_pair_name

  subnet_id                   = module.k3s_servers_vpc.public_subnets[0]
  vpc_security_group_ids      = [module.k3s_servers_security_group.security_group_id]
  associate_public_ip_address = true

  root_block_device = [{
    volume_size = 200
    volume_type = "gp2"
  }]

  monitoring = false
}

resource "null_resource" "k3s_server_installation_for_main_node" {
  triggers = {
    k3s_server_host              = module.k3s_servers[0].public_ip
    k3s_server_private_key       = module.k3s_servers_key_pair.private_key_pem
    k3s_server_main_ip           = local.k3s_server_main_ip
    k3s_version                  = var.k3s_version
    tailscale_k3s_main_server_ip = local.tailscale_k3s_main_server_ip
    tailscale_auth_key           = var.tailscale_auth_key
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    host        = self.triggers.k3s_server_host
    private_key = self.triggers.k3s_server_private_key
  }

  provisioner "file" {
    when        = create
    destination = "/tmp/k3s_server_install.sh"
    content = templatefile("${path.module}/scripts/k3s_server_install.sh.tpl", {
      k3s_version                  = self.triggers.k3s_version,
      k3s_token                    = null,
      k3s_server_main_ip           = self.triggers.k3s_server_main_ip,
      tailscale_k3s_main_server_ip = self.triggers.tailscale_k3s_main_server_ip,
      tailscale_k3s_server_ip      = self.triggers.tailscale_k3s_main_server_ip,
      tailscale_auth_key           = self.triggers.tailscale_auth_key,
      is_main_node                 = true,
    })
  }

  provisioner "remote-exec" {
    when = create
    inline = [
      "sh /tmp/k3s_server_install.sh"
    ]
  }

  provisioner "remote-exec" {
    when = destroy
    inline = [
      "/usr/local/bin/k3s-uninstall.sh"
    ]
  }
}

data "remote_file" "k3s_server_token" {
  conn {
    user        = "ubuntu"
    host        = module.k3s_servers[0].public_ip
    private_key = module.k3s_servers_key_pair.private_key_pem
    sudo        = true
    timeout     = 10000
  }

  path = "/var/lib/rancher/k3s/server/token"

  depends_on = [null_resource.k3s_server_installation_for_main_node]
}

resource "null_resource" "k3s_server_installation_for_additional_nodes" {
  for_each = { for server_idx, server_values in module.k3s_servers : server_idx => server_values if server_idx != 0 }

  triggers = {
    k3s_server_host              = each.value.public_ip
    k3s_server_private_key       = module.k3s_servers_key_pair.private_key_pem
    k3s_server_main_ip           = local.k3s_server_main_ip
    k3s_version                  = var.k3s_version
    k3s_token                    = local.k3s_token
    tailscale_k3s_main_server_ip = local.tailscale_k3s_main_server_ip
    tailscale_k3s_server_ip      = local.tailscale_k3s_additional_servers_ips[each.key]
    tailscale_auth_key           = var.tailscale_auth_key
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    host        = self.triggers.k3s_server_host
    private_key = self.triggers.k3s_server_private_key
  }

  provisioner "file" {
    when        = create
    destination = "/tmp/k3s_server_install.sh"
    content = templatefile("${path.module}/scripts/k3s_server_install.sh.tpl", {
      k3s_version                  = self.triggers.k3s_version,
      k3s_token                    = self.triggers.k3s_token,
      k3s_server_main_ip           = self.triggers.k3s_server_main_ip,
      tailscale_k3s_main_server_ip = self.triggers.tailscale_k3s_main_server_ip,
      tailscale_k3s_server_ip      = self.triggers.tailscale_k3s_server_ip,
      tailscale_auth_key           = self.triggers.tailscale_auth_key,
      is_main_node                 = false,
    })
  }

  provisioner "remote-exec" {
    when = create
    inline = [
      "sh /tmp/k3s_server_install.sh"
    ]
  }

  provisioner "remote-exec" {
    when = destroy
    inline = [
      "/usr/local/bin/k3s-uninstall.sh"
    ]
  }

  depends_on = [null_resource.k3s_server_installation_for_main_node]
}
