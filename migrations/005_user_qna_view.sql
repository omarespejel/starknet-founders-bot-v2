-- View that pairs each user message with the immediate next assistant response

CREATE OR REPLACE VIEW view_user_qna AS
WITH ordered AS (
    SELECT
        c.*,
        lead(c.role) OVER (PARTITION BY c.user_id, c.agent_type ORDER BY c.created_at) AS next_role,
        lead(c.id) OVER (PARTITION BY c.user_id, c.agent_type ORDER BY c.created_at) AS assistant_msg_id,
        lead(c.message) OVER (PARTITION BY c.user_id, c.agent_type ORDER BY c.created_at) AS assistant_response,
        lead(c.tokens_used) OVER (PARTITION BY c.user_id, c.agent_type ORDER BY c.created_at) AS assistant_tokens,
        lead(c.created_at) OVER (PARTITION BY c.user_id, c.agent_type ORDER BY c.created_at) AS assistant_created_at
    FROM conversations c
)
SELECT
    id AS user_msg_id,
    user_id,
    username,
    first_name,
    agent_type,
    message AS user_query,
    tokens_used AS user_tokens,
    created_at AS user_created_at,
    assistant_msg_id,
    assistant_response,
    assistant_tokens,
    assistant_created_at
FROM ordered
WHERE role = 'user' AND next_role = 'assistant';

