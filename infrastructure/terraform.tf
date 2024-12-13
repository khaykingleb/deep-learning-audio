terraform {
  required_version = ">= 1.8.6"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.34.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.16.1"
    }
    remote = {
      source  = "tenstad/remote"
      version = "~> 0.1.3"
    }
  }
}

provider "kubernetes" {
  host                   = module.k3s.kube_api_server
  client_certificate     = module.k3s.kube_client_certificate
  client_key             = module.k3s.kube_client_key
  cluster_ca_certificate = module.k3s.kube_cluster_ca_certificate
}

provider "helm" {
  kubernetes {
    host                   = module.k3s.kube_api_server
    client_certificate     = module.k3s.kube_client_certificate
    client_key             = module.k3s.kube_client_key
    cluster_ca_certificate = module.k3s.kube_cluster_ca_certificate
  }
}
