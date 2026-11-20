variable "project_id" {
  description = "Id of the Google Cloud admin project to create, e.g. box-admin-test-1234."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be 6-30 lowercase letters, digits or hyphens, starting with a letter."
  }
}

variable "project_name" {
  description = "Display name of the admin project."
  type        = string
  default     = "Box admin"
}

variable "org_id" {
  description = "Google Cloud organisation id (numeric) of the Workspace tenant."
  type        = string
}

variable "billing_account" {
  description = "Billing account id, XXXXXX-XXXXXX-XXXXXX."
  type        = string
}

variable "region" {
  description = "Region for the state bucket."
  type        = string
  default     = "us-central1"
}

variable "github_repository" {
  description = "owner/name of the GitHub repository whose workflows may act as the pipeline."
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$", var.github_repository))
    error_message = "github_repository must be owner/name."
  }
}

variable "environment" {
  description = "test or live, from company.yaml > workspace.environment."
  type        = string

  validation {
    condition     = contains(["test", "live"], var.environment)
    error_message = "environment must be test or live."
  }
}
