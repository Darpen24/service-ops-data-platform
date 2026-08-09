# Terraform infrastructure

This directory is a safe, opt-in design for the Snowflake and Databricks adapters. Start with
`terraform fmt -check -recursive`, then initialise without a real backend:

```bash
terraform -chdir=infrastructure/environments/dev init -backend=false
terraform -chdir=infrastructure/environments/dev validate
```

Copy `terraform.tfvars.example` to an uncommitted `terraform.tfvars` and set only approved values.
`terraform plan` requires valid provider authentication and is therefore not run automatically.
Never run `terraform apply` or `terraform destroy` from this project without separate human
approval and review. State can contain sensitive identifiers; production should use encrypted
remote state, least-privilege access, locking, separate environments, and audited import/drift
workflows. No remote backend is configured by default.
