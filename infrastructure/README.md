<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.8.6 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | ~> 2.16.1 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | ~> 2.34.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_grafana_cloud"></a> [grafana\_cloud](#module\_grafana\_cloud) | ./modules/grafana | n/a |
| <a name="module_k3s"></a> [k3s](#module\_k3s) | ./modules/k3s | n/a |
| <a name="module_k8s_monitoring"></a> [k8s\_monitoring](#module\_k8s\_monitoring) | ./modules/k8s/monitoring | n/a |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_enable_monitoring"></a> [enable\_monitoring](#input\_enable\_monitoring) | Enable Grafana Cloud monitoring. | `bool` | `false` | no |
| <a name="input_grafana_cloud_access_policy_token"></a> [grafana\_cloud\_access\_policy\_token](#input\_grafana\_cloud\_access\_policy\_token) | Grafana Cloud access policy token. | `string` | n/a | yes |
| <a name="input_grafana_cloud_stack_slug"></a> [grafana\_cloud\_stack\_slug](#input\_grafana\_cloud\_stack\_slug) | Grafana Cloud stack slug to use for monitoring. | `string` | n/a | yes |
| <a name="input_k3s_agents"></a> [k3s\_agents](#input\_k3s\_agents) | K3s agent nodes to deploy to the K3s cluster. | <pre>map(object({<br/>    host             = string<br/>    user             = string<br/>    private_key_name = string<br/>    provider         = string<br/>    labels           = optional(list(string), [])<br/>    taints           = optional(list(string), [])<br/>  }))</pre> | `{}` | no |
| <a name="input_k3s_servers_count"></a> [k3s\_servers\_count](#input\_k3s\_servers\_count) | Number of K3s servers to deploy to the cluster. | `number` | `1` | no |
| <a name="input_k3s_version"></a> [k3s\_version](#input\_k3s\_version) | Version of K3s to install on the nodes. See https://github.com/k3s-io/k3s/releases for available versions. | `string` | n/a | yes |
| <a name="input_shadeform_private_key"></a> [shadeform\_private\_key](#input\_shadeform\_private\_key) | Private key for Shadeform. | `string` | n/a | yes |
| <a name="input_tailscale_auth_key"></a> [tailscale\_auth\_key](#input\_tailscale\_auth\_key) | Reusable and ephemeral Tailscale auth key to join the nodes to build a mesh between the nodes via the Tailscale VPN. Needs to have the tag `k3s-cluster`. | `string` | n/a | yes |
| <a name="input_tailscale_oauth_id"></a> [tailscale\_oauth\_id](#input\_tailscale\_oauth\_id) | Tailscale OAuth client ID. | `string` | n/a | yes |
| <a name="input_tailscale_oauth_secret"></a> [tailscale\_oauth\_secret](#input\_tailscale\_oauth\_secret) | Tailscale OAuth client secret. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_k3s_servers_ips"></a> [k3s\_servers\_ips](#output\_k3s\_servers\_ips) | IP addresses of the K3s server nodes. |
| <a name="output_k3s_servers_private_key"></a> [k3s\_servers\_private\_key](#output\_k3s\_servers\_private\_key) | Private key for SSH access to the K3s server nodes. |
| <a name="output_kube_api_server"></a> [kube\_api\_server](#output\_kube\_api\_server) | API server of the K3s cluster. |
| <a name="output_kubeconfig"></a> [kubeconfig](#output\_kubeconfig) | Kubeconfig in YAML format |
<!-- END_TF_DOCS -->