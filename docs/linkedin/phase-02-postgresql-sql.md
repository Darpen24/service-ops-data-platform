# LinkedIn draft: PostgreSQL and SQL analytics

I completed the local PostgreSQL and SQL phase of my Service Operations Data Platform portfolio.
It loads deterministic, typed Parquet service-ticket data into a constrained PostgreSQL raw layer,
records the source checksum, and exposes reusable analytics views. The load is transactional and
idempotent, while SQL validation checks lifecycle, relationships, SLA mapping, and assigned-team
quality rules.

The project includes twenty executable service-operations questions covering backlog, SLA breaches,
mean and median resolution time, recurrence, trends, rankings, and lifecycle duration. I also added
integration tests and query-plan guidance. Next is the explicitly separate ETL/ELT and data-quality
phase—no cloud claims or employer data involved.
