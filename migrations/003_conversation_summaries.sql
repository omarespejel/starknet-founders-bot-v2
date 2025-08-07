-- Add conversation summaries and metadata
ALTER TABLE conversations 
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

ALTER TABLE user_sessions
ADD COLUMN IF NOT EXISTS conversation_context JSONB DEFAULT '{}';

-- Index for faster JSON queries
CREATE INDEX IF NOT EXISTS idx_conversations_metadata ON conversations USING GIN (metadata);
