terraform {
  required_version = ">= 1.0.0"

  required_providers {
    ec = {
      source  = "elastic/ec"
      version = ">=0.12.3,<1.0"
    }
    elasticstack = {
      source  = "elastic/elasticstack"
      version = "~>0.9"
    }
  }
}
