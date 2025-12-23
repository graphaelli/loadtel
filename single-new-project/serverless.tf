resource "ec_observability_project" "loadsingle" {
  name      = "loadsingle-${formatdate("YYYYMMDD-HHmmss", timestamp())}"
  region_id = var.region_id
  lifecycle {
    ignore_changes = [name]
  }
}

output "es_url" {
  value = ec_observability_project.loadsingle.endpoints.elasticsearch
}

output "kibana_url" {
  value = ec_observability_project.loadsingle.endpoints.kibana
}

output "ingest_url" {
  value = ec_observability_project.loadsingle.endpoints.ingest
}
    
output "cloud_id" {
  value = ec_observability_project.loadsingle.cloud_id
}

output "project_id" {
  value = ec_observability_project.loadsingle.id
}

output "es_username" {
  value = ec_observability_project.loadsingle.credentials.username
}

output "es_password" {
  value = ec_observability_project.loadsingle.credentials.password
  sensitive = true
}
