-- Analytics table for tracking bot usage
-- This file contains the schema for bot analytics and usage tracking

-- Bot analytics table to store user interaction events
CREATE TABLE IF NOT EXISTS bot_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance on analytics queries
CREATE INDEX IF NOT EXISTS idx_bot_analytics_user_id ON bot_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_bot_analytics_action ON bot_analytics(action);
CREATE INDEX IF NOT EXISTS idx_bot_analytics_created_at ON bot_analytics(created_at);
CREATE INDEX IF NOT EXISTS idx_bot_analytics_user_action ON bot_analytics(user_id, action);

-- Analytics events that will be tracked:
-- - bot_started: When user first starts the bot
-- - agent_selected: When user selects PM or VC agent
-- - agent_switched: When user switches between agents  
-- - message_processed: When user sends message and gets AI response
-- - message_error: When message processing fails
-- - conversation_reset: When user resets conversation history
-- - stats_viewed: When user checks their statistics
-- - rate_limited: When user hits rate limit (optional enhancement)
