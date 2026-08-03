CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

COMMENT ON SCHEMA raw IS 'Typed source-aligned Phase 1 records.';
COMMENT ON SCHEMA staging IS 'Reserved for future cleaning and standardisation.';
COMMENT ON SCHEMA analytics IS 'Phase 2 reporting views; dbt will formalise this later.';
COMMENT ON SCHEMA audit IS 'Minimal local sample-load metadata.';
