CREATE TABLE IF NOT EXISTS audit.pipeline_runs (
    run_id UUID PRIMARY KEY,
    source_name TEXT NOT NULL,
    batch_id TEXT NOT NULL,
    source_checksum TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'succeeded', 'failed', 'partial')),
    watermark_before TIMESTAMPTZ,
    watermark_after TIMESTAMPTZ,
    inserted_count INTEGER NOT NULL DEFAULT 0 CHECK (inserted_count >= 0),
    updated_count INTEGER NOT NULL DEFAULT 0 CHECK (updated_count >= 0),
    quarantined_count INTEGER NOT NULL DEFAULT 0 CHECK (quarantined_count >= 0),
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS audit.pipeline_watermarks (
    source_name TEXT PRIMARY KEY,
    watermark_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit.quarantine_records (
    quarantine_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES audit.pipeline_runs (run_id),
    source_name TEXT NOT NULL,
    batch_id TEXT NOT NULL,
    record_identifier TEXT,
    rule_name TEXT NOT NULL,
    reason TEXT NOT NULL,
    raw_payload JSONB NOT NULL,
    quarantined_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS staging.ticket_ingest (
    batch_id TEXT NOT NULL,
    ticket_id TEXT NOT NULL,
    source_updated_at TIMESTAMPTZ NOT NULL,
    record_checksum TEXT NOT NULL,
    payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (batch_id, ticket_id)
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_source_batch
    ON audit.pipeline_runs (source_name, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_quarantine_run ON audit.quarantine_records (run_id);
CREATE INDEX IF NOT EXISTS idx_ticket_ingest_updated ON staging.ticket_ingest (source_updated_at);
