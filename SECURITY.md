# Security policy

## Supported state

Phase 0 supports local development only. It contains no production deployment, cloud resource, or real operational data.

## Secrets

Never commit `.env`, tokens, passwords, API keys, private keys, or full connection strings. Use `.env.example` only for non-sensitive local defaults. Immediately rotate any secret that is accidentally exposed and remove it from Git history with an approved remediation process.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Contact the repository owner privately with affected component, impact, reproduction steps, and any suggested mitigation. Do not include secrets in the report.

## Local PostgreSQL

The Compose password is explicitly local-development-only. Do not expose the configured port beyond trusted local networks, and do not reuse the example password outside this project.
