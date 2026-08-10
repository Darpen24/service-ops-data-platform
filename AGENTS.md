# Repository instructions

Before changing this repository, read `PLANS.md`, `DECISIONS.md`, and `IMPLEMENTATION_LOG.md`. Keep each change scoped to the active phase; do not begin a later phase early.

- Run relevant validation after every logical change and record actual results.
- Never expose, commit, or log secrets, tokens, passwords, or connection strings.
- Update documentation whenever user-facing behaviour or developer workflows change.
- Do not rewrite working components without a documented reason.
- Record material design decisions in `DECISIONS.md` and failed approaches in `IMPLEMENTATION_LOG.md`.
- Use conventional commit messages when commits are requested.
- Never fabricate cloud execution, deployment, test results, or screenshots.
- Preserve backward compatibility unless the current plan explicitly changes it.
- Keep functions small, typed, testable, and free of business logic not planned for the current phase.

## Current phase boundary

Phase 6 may implement optional Snowflake adapter scripts and credential-aware configuration. Do
not create cloud resources, add Databricks, Terraform, Airflow, or Power BI artifacts early.
