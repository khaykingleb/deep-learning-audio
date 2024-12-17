<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.8.6 |
| <a name="requirement_tailscale"></a> [tailscale](#requirement\_tailscale) | ~> 0.17.2 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_tailscale"></a> [tailscale](#provider\_tailscale) | 0.17.2 |

## Resources

| Name | Type |
|------|------|
| [tailscale_acl.acl](https://registry.terraform.io/providers/tailscale/tailscale/latest/docs/resources/acl) | resource |
| [tailscale_tailnet_key.k3s_cluster](https://registry.terraform.io/providers/tailscale/tailscale/latest/docs/resources/tailnet_key) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_tailscale_oauth_id"></a> [tailscale\_oauth\_id](#input\_tailscale\_oauth\_id) | Tailscale OAuth client ID. | `string` | n/a | yes |
| <a name="input_tailscale_oauth_secret"></a> [tailscale\_oauth\_secret](#input\_tailscale\_oauth\_secret) | Tailscale OAuth client secret. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_k3s_cluster_auth_key"></a> [k3s\_cluster\_auth\_key](#output\_k3s\_cluster\_auth\_key) | Auth key for Tailscale VPN in K3s cluster |
<!-- END_TF_DOCS -->