terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0, < 9.0"
    }
  }

  # First apply runs with local state (see ../README.md). After it, copy
  # backend.tf.example to backend.tf and run `terraform init -migrate-state`.
}

provider "google" {
  region                = var.region
  user_project_override = true
  billing_project       = var.project_id
}
