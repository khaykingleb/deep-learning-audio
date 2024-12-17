<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.8.6 |
| <a name="requirement_grafana"></a> [grafana](#requirement\_grafana) | ~> 3.15.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_grafana.cloud"></a> [grafana.cloud](#provider\_grafana.cloud) | ~> 3.15.0 |
| <a name="provider_grafana.stack"></a> [grafana.stack](#provider\_grafana.stack) | ~> 3.15.0 |

## Resources

| Name | Type |
|------|------|
| [grafana_cloud_access_policy.grafana_alloy](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/cloud_access_policy) | resource |
| [grafana_cloud_access_policy_token.grafana_alloy](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/cloud_access_policy_token) | resource |
| [grafana_cloud_stack_service_account.cloud_sa](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/cloud_stack_service_account) | resource |
| [grafana_cloud_stack_service_account_token.cloud_sa](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/cloud_stack_service_account_token) | resource |
| [grafana_dashboard.gpu](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/dashboard) | resource |
| [grafana_dashboard.k8s_global](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/dashboard) | resource |
| [grafana_dashboard.k8s_namespaces](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/dashboard) | resource |
| [grafana_dashboard.k8s_nodes](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/dashboard) | resource |
| [grafana_dashboard.k8s_pods](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/dashboard) | resource |
| [grafana_folder.general](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/folder) | resource |
| [grafana_folder.kubernetes](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/folder) | resource |
| [grafana_cloud_stack.this](https://registry.terraform.io/providers/grafana/grafana/latest/docs/data-sources/cloud_stack) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_enable_monitoring"></a> [enable\_monitoring](#input\_enable\_monitoring) | Enable Grafana Cloud monitoring. | `bool` | `false` | no |
| <a name="input_grafana_cloud_access_policy_token"></a> [grafana\_cloud\_access\_policy\_token](#input\_grafana\_cloud\_access\_policy\_token) | Grafana Cloud access policy token. | `string` | n/a | yes |
| <a name="input_grafana_cloud_stack_slug"></a> [grafana\_cloud\_stack\_slug](#input\_grafana\_cloud\_stack\_slug) | Grafana Cloud stack slug. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_alloy_access_token"></a> [alloy\_access\_token](#output\_alloy\_access\_token) | Grafana Alloy access token. |
| <a name="output_loki_url"></a> [loki\_url](#output\_loki\_url) | Grafana Cloud Loki URL. |
| <a name="output_loki_user_id"></a> [loki\_user\_id](#output\_loki\_user\_id) | Grafana Cloud Loki user ID. |
| <a name="output_prometheus_url"></a> [prometheus\_url](#output\_prometheus\_url) | Grafana Cloud Prometheus URL. |
| <a name="output_prometheus_user_id"></a> [prometheus\_user\_id](#output\_prometheus\_user\_id) | Grafana Cloud Prometheus user ID. |
<!-- END_TF_DOCS -->
