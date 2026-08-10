# Phase 6: optional Snowflake adapter

Snowflake remains an optional adapter; PostgreSQL stays the runnable local platform. The scripts
define a small database/schema/warehouse/role baseline, a Parquet file format and stage, VARIANT
event example, stream, and a suspended task. All identifiers are deliberately small and the
warehouse auto-suspends after 60 seconds to control cost.

Credentials exist only as environment variables in the dbt profile example: account, user,
authenticator, role, warehouse, database, and schema. No Snowflake command was executed because
credentials were not supplied. Time Travel and zero-copy cloning are operational features to use
only after approved data exists; their value is safe recovery/testing without duplicating storage.

Interview prompts: storage/compute separation allows independent scaling; micro-partitions make
many scans efficient; stages and COPY separate file landing from loading; streams record change
data; tasks schedule transformations; resource monitors and auto-suspend constrain spend.
