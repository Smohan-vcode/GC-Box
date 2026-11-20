output "pipeline_client_id" {
  description = "Numeric client id for domain-wide delegation (runbook M-15)."
  value       = google_service_account.pipeline.unique_id
}

output "pipeline_service_account" {
  description = "Service account email; GitHub variable GCP_SERVICE_ACCOUNT."
  value       = google_service_account.pipeline.email
}

output "workload_identity_provider" {
  description = "Full provider name; GitHub variable GCP_WORKLOAD_IDENTITY_PROVIDER."
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "state_bucket" {
  description = "GCS bucket for Terraform state; GitHub variable TF_STATE_BUCKET."
  value       = google_storage_bucket.state.name
}

output "project_id" {
  value = google_project.admin.project_id
}
