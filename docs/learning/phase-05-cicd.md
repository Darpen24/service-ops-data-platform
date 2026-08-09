# Phase 5: CI/CD quality gates

`.github/workflows/quality.yml` runs for pull requests and `main` pushes. It uses Python 3.12,
a PostgreSQL service container, dependency caching, formatting/lint/type/test/coverage checks,
SQLFluff, Compose configuration, Phase 2 sample loading, dbt parse/build, and a separate
Gitleaks secret scan. The workflow has read-only default permissions and grants security-events
write only to the scanner.

CI continuously verifies each change; continuous delivery would make an approved artifact ready
for release, but this project does not automatically deploy cloud resources. A service container
keeps integration tests isolated. Artifacts retain the coverage report. Rollback means reverting a
merged commit or closing a draft PR; credentials remain GitHub secrets, never repository files.

Remote workflow execution is pending GitHub Actions after this configuration is pushed. No remote
workflow success is claimed in this repository until GitHub reports it.
