# Terraform

| Module | Track | Manages |
| --- | --- | --- |
| `gcp/` | T0-03 | Admin project, APIs, pipeline service account, workload identity federation for GitHub, state bucket |
| `dns/` | T2 | Cloudflare records (not yet written) |
| `groups/` | T1 | Reserved |

Terraform >= 1.9. Providers are pinned in each module's `.terraform.lock.hcl`.
No module holds a company-specific value: values come from `terraform.tfvars`
(git-ignored) or from the pipeline.

## gcp: first apply (human step in T0-03)

Run once per environment (test, then live) by someone with these rights in
the tenant's Google Cloud organisation: Project Creator, Billing Account
User on the billing account, and Organization Viewer.

1. Sign in with owner credentials:

   ```bash
   gcloud auth application-default login
   ```

2. Fill in values:

   ```bash
   cd engine/terraform/gcp
   cp terraform.tfvars.example terraform.tfvars
   ```

   `org_id` comes from `gcloud organizations list`, `billing_account` from
   `gcloud billing accounts list`, `environment` from `company.yaml >
   workspace.environment`.

3. Apply with local state:

   ```bash
   terraform init
   terraform plan -out tfplan
   terraform apply tfplan
   ```

4. Move state into the bucket the apply created:

   ```bash
   cp backend.tf.example backend.tf
   terraform init -migrate-state -backend-config="bucket=$(terraform output -raw state_bucket)"
   ```

   Then delete the local `terraform.tfstate*` files.

5. Record the outputs:

   | Output | Goes to |
   | --- | --- |
   | `pipeline_client_id` | Runbook M-15: Admin console, Security, API controls, Domain-wide delegation, with the scopes in `expected-state/dwd-scopes.yaml` |
   | `workload_identity_provider` | GitHub repository variable `GCP_WORKLOAD_IDENTITY_PROVIDER` |
   | `pipeline_service_account` | GitHub repository variable `GCP_SERVICE_ACCOUNT` |
   | `state_bucket` | GitHub repository variable `TF_STATE_BUCKET` |
   | `project_id` | GitHub repository variable `GCP_PROJECT_ID` |

   These are identifiers, not secrets. No key is created or stored.

## Exit check for T0-03

From a GitHub Actions run on this repository (T0-04 adds the workflow), the
pipeline authenticates through workload identity federation and lists the
state bucket:

```bash
gcloud storage ls "gs://$TF_STATE_BUCKET"
```

## Later applies

Pipeline only (`.github/workflows/apply.yml`), with
`-backend-config="bucket=$TF_STATE_BUCKET"`.
