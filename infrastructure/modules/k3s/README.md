<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.8.6 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 5.80.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | ~> 3.2.3 |
| <a name="requirement_random"></a> [random](#requirement\_random) | ~> 3.6.3 |
| <a name="requirement_remote"></a> [remote](#requirement\_remote) | ~> 0.1.3 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 5.80.0 |
| <a name="provider_null"></a> [null](#provider\_null) | 3.2.3 |
| <a name="provider_random"></a> [random](#provider\_random) | 3.6.3 |
| <a name="provider_remote"></a> [remote](#provider\_remote) | 0.1.3 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_k3s_servers"></a> [k3s\_servers](#module\_k3s\_servers) | terraform-aws-modules/ec2-instance/aws | ~> 5.7.1 |
| <a name="module_k3s_servers_key_pair"></a> [k3s\_servers\_key\_pair](#module\_k3s\_servers\_key\_pair) | terraform-aws-modules/key-pair/aws | ~> 2.0.3 |
| <a name="module_k3s_servers_security_group"></a> [k3s\_servers\_security\_group](#module\_k3s\_servers\_security\_group) | terraform-aws-modules/security-group/aws | ~> 5.2.0 |
| <a name="module_k3s_servers_vpc"></a> [k3s\_servers\_vpc](#module\_k3s\_servers\_vpc) | terraform-aws-modules/vpc/aws | ~> 5.16.0 |

## Resources

| Name | Type |
|------|------|
| [null_resource.k3s_installation_for_agents](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [null_resource.k3s_server_installation_for_additional_nodes](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [null_resource.k3s_server_installation_for_main_node](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [null_resource.tailscale_activation_for_k3s_agents](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [null_resource.tailscale_activation_for_k3s_servers](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [random_string.k3s_token](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [aws_availability_zones.available](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones) | data source |
| [remote_file.k3s_main_server_tailscale_ip](https://registry.terraform.io/providers/tenstad/remote/latest/docs/data-sources/file) | data source |
| [remote_file.kubeconfig](https://registry.terraform.io/providers/tenstad/remote/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | AWS region to deploy the K3s servers in. | `string` | `"us-east-1"` | no |
| <a name="input_k3s_agents"></a> [k3s\_agents](#input\_k3s\_agents) | K3s agent nodes to deploy to the K3s cluster. | <pre>map(object({<br/>    host             = string<br/>    user             = string<br/>    private_key_name = string<br/>    provider         = string<br/>    labels           = optional(list(string), [])<br/>    taints           = optional(list(string), [])<br/>  }))</pre> | `{}` | no |
| <a name="input_k3s_servers_count"></a> [k3s\_servers\_count](#input\_k3s\_servers\_count) | Number of K3s servers to deploy to the cluster. | `number` | `1` | no |
| <a name="input_k3s_version"></a> [k3s\_version](#input\_k3s\_version) | Version of K3s to install on the nodes. See https://github.com/k3s-io/k3s/releases for available versions. | `string` | n/a | yes |
| <a name="input_shadeform_private_key"></a> [shadeform\_private\_key](#input\_shadeform\_private\_key) | Private key for Shadeform. | `string` | n/a | yes |
| <a name="input_tailscale_auth_key"></a> [tailscale\_auth\_key](#input\_tailscale\_auth\_key) | Reusable and ephemeral Tailscale auth key to build a mesh via Tailscale VPN in the K3s cluster. Needs to have the tag `k3s-cluster`. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_kube_api_server"></a> [kube\_api\_server](#output\_kube\_api\_server) | Kube API server for the K3s cluster. |
| <a name="output_kube_client_certificate"></a> [kube\_client\_certificate](#output\_kube\_client\_certificate) | Client certificate for the K3s cluster. |
| <a name="output_kube_client_key"></a> [kube\_client\_key](#output\_kube\_client\_key) | Client key for the K3s cluster. |
| <a name="output_kube_cluster_ca_certificate"></a> [kube\_cluster\_ca\_certificate](#output\_kube\_cluster\_ca\_certificate) | Cluster CA certificate for the K3s cluster. |
| <a name="output_kubeconfig"></a> [kubeconfig](#output\_kubeconfig) | Kubeconfig file for the K3s cluster. |
| <a name="output_servers_ips"></a> [servers\_ips](#output\_servers\_ips) | IP addresses of the K3s server nodes. |
| <a name="output_servers_private_key"></a> [servers\_private\_key](#output\_servers\_private\_key) | Private key for SSH access to the K3s server nodes. |
<!-- END_TF_DOCS -->