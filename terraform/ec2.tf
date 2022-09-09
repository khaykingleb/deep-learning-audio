resource "aws_key_pair" "this" {
  public_key      = chomp(tls_private_key.ssh.public_key_openssh)
  key_name_prefix = local.full_project_name

  tags = merge({ name = "DLA-SSH-Key" }, local.tags)
}

resource "aws_instance" "this" {
  ami             = var.ami_id
  instance_type   = var.instance_type
  subnet_id       = aws_subnet.this.id
  security_groups = [aws_security_group.this.id]
  key_name        = aws_key_pair.this.key_name

  tags = merge({ name = "DLA-EC2" }, local.tags)
}

resource "aws_eip" "this" {
  instance = aws_instance.this.id
  vpc      = true
}
