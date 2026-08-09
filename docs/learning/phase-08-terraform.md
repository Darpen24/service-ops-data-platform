# Phase 8: Terraform infrastructure as code

`infrastructure/` contains version-pinned Snowflake and Databricks modules plus an opt-in `dev`
environment. Variables are typed, described, validated, and sensitive where appropriate. The
Snowflake module models a one-day-retention database/schema and auto-suspending warehouse; the
Databricks module models a cost-guard cluster policy, not a running cluster.

Terraform state maps declared resources to real infrastructure. Local validation uses no backend;
team use needs encrypted remote state, locking, least-privilege access, separate environments, and
careful import/drift review. Plans show intended changes; apply changes infrastructure and must be
approved by a human. Destroy is equally destructive and is never automated here.

Run `fmt`, `init -backend=false`, and `validate` before an authenticated plan. Provider
authentication comes from uncommitted variables/environment settings. `terraform apply` and
`terraform destroy` were not run and are prohibited in this autonomous implementation.
