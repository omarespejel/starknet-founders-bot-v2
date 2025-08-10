-- Read-friendly view for exporting user queries
-- Creates a view that selects only user-side messages with useful derived fields

CREATE OR REPLACE VIEW view_user_queries AS
SELECT
    c.id,
    c.user_id,
    c.username,
    c.first_name,
    c.agent_type,
    c.message AS query,
    c.tokens_used,
    c.created_at,
    length(c.message) AS message_length,
    date_trunc('day', c.created_at) AS day,
    date_trunc('hour', c.created_at) AS hour
FROM conversations c
WHERE c.role = 'user';

-- Optional: if you need a materialized view for very large datasets, create it instead
-- and remember to REFRESH MATERIALIZED VIEW periodically.

