CREATE TABLE IF NOT EXISTS audit.sample_loads (
    load_id BIGSERIAL PRIMARY KEY,
    generated_batch_id TEXT NOT NULL UNIQUE,
    manifest_checksum TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.teams (
    team_id TEXT PRIMARY KEY,
    team_name TEXT NOT NULL,
    region TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.agents (
    agent_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    team_id TEXT NOT NULL REFERENCES raw.teams (team_id),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    business_unit TEXT NOT NULL,
    region TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.categories (
    category_id TEXT PRIMARY KEY,
    category_name TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.subcategories (
    subcategory_id TEXT PRIMARY KEY,
    subcategory_name TEXT NOT NULL,
    category_id TEXT NOT NULL REFERENCES raw.categories (category_id),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.sla_rules (
    sla_rule_id TEXT PRIMARY KEY,
    priority TEXT NOT NULL UNIQUE CHECK (priority IN ('P1', 'P2', 'P3', 'P4')),
    target_hours INTEGER NOT NULL CHECK (target_hours > 0),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.tickets (
    ticket_id TEXT PRIMARY KEY,
    ticket_type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    first_response_at TIMESTAMPTZ NOT NULL,
    in_progress_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    priority TEXT NOT NULL CHECK (priority IN ('P1', 'P2', 'P3', 'P4')),
    impact TEXT NOT NULL,
    urgency TEXT NOT NULL,
    category_id TEXT NOT NULL REFERENCES raw.categories (category_id),
    subcategory_id TEXT NOT NULL REFERENCES raw.subcategories (subcategory_id),
    assigned_team_id TEXT NOT NULL REFERENCES raw.teams (team_id),
    assigned_agent_id TEXT NOT NULL REFERENCES raw.agents (agent_id),
    customer_id TEXT NOT NULL REFERENCES raw.customers (customer_id),
    business_unit TEXT NOT NULL,
    region TEXT NOT NULL,
    channel TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('new', 'assigned', 'in_progress', 'resolved', 'closed')),
    sla_target_hours INTEGER NOT NULL CHECK (sla_target_hours > 0),
    first_response_minutes INTEGER NOT NULL CHECK (first_response_minutes >= 0),
    resolution_minutes INTEGER CHECK (resolution_minutes >= 0),
    reopened_count INTEGER NOT NULL CHECK (reopened_count >= 0),
    escalation_count INTEGER NOT NULL CHECK (escalation_count >= 0),
    satisfaction_score INTEGER CHECK (satisfaction_score BETWEEN 1 AND 5),
    short_description TEXT NOT NULL,
    source_system TEXT NOT NULL,
    generated_batch_id TEXT NOT NULL,
    CHECK (assigned_agent_id IS NOT NULL),
    CHECK (created_at <= first_response_at),
    CHECK (first_response_at <= in_progress_at),
    CHECK (resolved_at IS NULL OR in_progress_at <= resolved_at),
    CHECK (resolved_at IS NULL OR resolved_at >= created_at),
    CHECK (closed_at IS NULL OR (resolved_at IS NOT NULL AND closed_at >= resolved_at)),
    CHECK (
        resolved_at IS NOT NULL
        OR (closed_at IS NULL AND resolution_minutes IS NULL AND satisfaction_score IS NULL)
    ),
    CHECK (updated_at >= coalesce(closed_at, resolved_at, in_progress_at))
);
CREATE TABLE IF NOT EXISTS raw.ticket_status_history (
    status_event_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES raw.tickets (ticket_id),
    status TEXT NOT NULL CHECK (status IN ('new', 'assigned', 'in_progress', 'resolved', 'closed')),
    changed_at TIMESTAMPTZ NOT NULL,
    sequence INTEGER NOT NULL CHECK (sequence > 0),
    UNIQUE (ticket_id, sequence)
);
