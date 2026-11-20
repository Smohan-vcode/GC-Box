locals {
  # Workspace APIs the box CLI, GAM7 and the cockpit call, plus what
  # workload identity federation and the state bucket need.
  services = [
    "admin.googleapis.com",
    "groupssettings.googleapis.com",
    "gmail.googleapis.com",
    "drive.googleapis.com",
    "drivelabels.googleapis.com",
    "cloudidentity.googleapis.com",
    "script.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
    "storage.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
  ]
  labels = {
    managed-by  = "terraform"
    component   = "box-pipeline"
    environment = var.environment
  }
}

resource "google_project" "admin" {
  project_id      = var.project_id
  name            = var.project_name
  org_id          = var.org_id
  billing_account = var.billing_account
  labels          = local.labels
  deletion_policy = "PREVENT"
}

resource "google_project_service" "enabled" {
  for_each           = toset(local.services)
  project            = google_project.admin.project_id
  service            = each.value
  disable_on_destroy = false
}

# The identity GitHub Actions runs as. It holds no key: workflows obtain
# short-lived tokens through workload identity federation, and act in
# the tenant through domain-wide delegation (runbook M-15).
resource "google_service_account" "pipeline" {
  project      = google_project.admin.project_id
  account_id   = "box-pipeline"
  display_name = "Box pipeline (${var.environment})"
  description  = "Used by GitHub Actions through workload identity federation. No keys."
  depends_on   = [google_project_service.enabled]
}

# Domain-wide delegation needs the account to sign its own JWTs.
resource "google_service_account_iam_member" "pipeline_self_sign" {
  service_account_id = google_service_account.pipeline.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_iam_workload_identity_pool" "github" {
  project                   = google_project.admin.project_id
  workload_identity_pool_id = "github"
  display_name              = "GitHub Actions"
  depends_on                = [google_project_service.enabled]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = google_project.admin.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-oidc"
  display_name                       = "GitHub OIDC"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }
  # Only this repository's workflows can exchange tokens.
  attribute_condition = "assertion.repository == \"${var.github_repository}\""

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "pipeline_wif" {
  service_account_id = google_service_account.pipeline.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repository}"
}

resource "google_storage_bucket" "state" {
  project                     = google_project.admin.project_id
  name                        = "${var.project_id}-tfstate"
  location                    = upper(var.region)
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  labels                      = local.labels

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 20
      with_state         = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.enabled]
}

resource "google_storage_bucket_iam_member" "pipeline_state" {
  bucket = google_storage_bucket.state.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline.email}"
}

# Listing the bucket is the T0-03 exit check.
resource "google_storage_bucket_iam_member" "pipeline_state_reader" {
  bucket = google_storage_bucket.state.name
  role   = "roles/storage.legacyBucketReader"
  member = "serviceAccount:${google_service_account.pipeline.email}"
}
