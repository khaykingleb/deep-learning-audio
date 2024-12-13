# https://github.com/terraform-linters/tflint/tree/master/docs/user-guide

config {
  call_module_type = "local"  # Enable local module inspection
}

#@ Plugins
plugin "terraform" {
  enabled = true
  version = "0.4.0"
  source  = "github.com/terraform-linters/tflint-ruleset-terraform"
}

plugin "aws" {
    enabled = true
    version = "0.27.0"
    source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

#@ Rules
## Disallow // comments in favor of #.
rule "terraform_comment_syntax" {
  enabled = true
}

## Enforce naming conventions
rule "terraform_naming_convention" {
  enabled = true
}

## Disallow output declarations without description
rule "terraform_documented_outputs" {
  enabled = true
}

## Disallow variable declarations without description
rule "terraform_documented_variables" {
  enabled = true
}

## Disallow variable declarations without type
rule "terraform_typed_variables" {
  enabled = true
}

## Disallow variables, data sources, and locals that are declared but never used
rule "terraform_unused_declarations" {
  enabled = true
}

# Ensure that a module complies with the Terraform Standard Module Structure
rule "terraform_standard_module_structure" {
  enabled = true
}

# Disallow legacy dot index syntax
rule "terraform_deprecated_index" {
  enabled = true
}

## Disallow unused providers
rule "terraform_unused_required_providers" {
  enabled = true
}
