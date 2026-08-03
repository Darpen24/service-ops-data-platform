CREATE OR REPLACE VIEW analytics.dim_team AS SELECT
    team_id,
    team_name,
    region
FROM raw.teams;
CREATE OR REPLACE VIEW analytics.dim_agent AS SELECT
    agent_id,
    agent_name,
    team_id
FROM raw.agents;
CREATE OR REPLACE VIEW analytics.dim_customer AS
SELECT
    customer_id,
    customer_name,
    business_unit,
    region
FROM raw.customers;
CREATE OR REPLACE VIEW analytics.dim_category AS
SELECT
    s.subcategory_id,
    s.subcategory_name,
    c.category_id,
    c.category_name
FROM raw.subcategories AS s
INNER JOIN raw.categories AS c ON s.category_id = c.category_id;
CREATE OR REPLACE VIEW analytics.dim_priority AS
SELECT
priority,
target_hours AS sla_target_hours
FROM raw.sla_rules;
CREATE OR REPLACE VIEW analytics.dim_date AS
SELECT DISTINCT created_at::date AS date_key
FROM raw.tickets;
CREATE OR REPLACE VIEW analytics.fct_tickets AS SELECT * FROM raw.tickets;
CREATE OR REPLACE VIEW analytics.fct_ticket_status_events AS
SELECT *
FROM raw.ticket_status_history;
