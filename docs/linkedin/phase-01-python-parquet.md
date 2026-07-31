# Draft: deterministic service-operations source data

I implemented a deterministic Python source-data generator for a Service Operations Data Platform. It creates related tickets, teams, agents, customers, categories, SLA rules, and status history, then writes JSON, CSV, and Snappy Parquet with a reproducibility manifest.

The useful lesson was that reproducibility is more than setting a seed: configuration, reference relationships, output schemas, and validation rules must all remain stable. I also kept intentional data-quality defects separate from clean output so later quality work is demonstrable without making the default pipeline unreliable.

One challenge was preserving realistic ticket lifecycles while keeping timestamps UTC-aware and foreign keys valid. The design uses focused modules and temporary-directory integration tests to keep that boundary clear.

Suggested visual: the generator-to-formats flow or the tickets-to-status-history relationship. Repository link: `<repository-link>`.

How do you balance realistic synthetic data behaviour with deterministic, reviewable tests?
