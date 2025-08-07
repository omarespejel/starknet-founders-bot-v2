# 🚀 Deployment Guide for Starknet Startup Advisor Bot

## ✅ Production Features Added

### 🛡️ Rate Limiting
- **Limit**: 30 messages per user per hour
- **Protection**: Prevents API abuse and ensures fair usage
- **User Experience**: Clear error messages with wait times

### 🔧 Error Handling
- **Global Error Handler**: Catches all unhandled exceptions
- **User-Friendly Messages**: No technical errors exposed to users
- **Comprehensive Logging**: All errors logged for debugging

### 📊 Monitoring Ready
- **Structured Logging**: Production-ready log format
- **Environment Variables**: All secrets externalized
- **Health Checks**: Bot connection verification scripts

## 🎯 Deployment Options

### Option A: Render.com (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add production features for deployment"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - New > Blueprint
   - Connect your GitHub repo
   - Add environment variables:
     - `TELEGRAM_BOT_TOKEN`
     - `OPENROUTER_API_KEY`
     - `SUPABASE_URL`
     - `SUPABASE_SERVICE_KEY`
   - Deploy!

### Option B: Other Platforms

Use the included `Procfile` and `requirements.txt` for:
- Heroku
- Railway
- DigitalOcean App Platform
- Any platform supporting Python workers

## 📋 Pre-Deployment Checklist

- [x] ✅ Bot connects to Telegram API
- [x] ✅ OpenRouter API working with Sonar Pro model
- [x] ✅ Supabase database connected
- [x] ✅ Rate limiting implemented
- [x] ✅ Error handling added
- [x] ✅ Production logging configured
- [x] ✅ Dependencies exported (requirements.txt)
- [x] ✅ Deployment config ready (render.yaml)

## 🎨 Production Features

### 🔄 Rate Limiting
- 30 messages per hour per user
- Automatic cleanup of old requests
- User-friendly rate limit messages

### 🛠️ Error Handling
- Global exception handler
- Graceful error messages
- Comprehensive error logging

### 📈 Scalability Ready
- In-memory rate limiting (suitable for single instance)
- Environment-based configuration
- Production logging format

## 🧪 Testing Commands

```bash
# Test bot connection
uv run python scripts/test_telegram_bot.py

# Test OpenRouter API
uv run python scripts/test_openrouter.py

# Test Supabase connection
uv run python scripts/test_supabase.py

# Run the bot locally
uv run python -m src.bot.main
```

## 📊 Analytics & Monitoring

### Analytics Features Added
- **User Activity Tracking**: All major user actions logged
- **Performance Metrics**: Response times, token usage, error rates
- **Agent Preferences**: Track which AI personalities are most popular
- **Error Monitoring**: Automatic logging of failures and rate limits

### Analytics Events Tracked
- `bot_started`: New user onboarding
- `agent_selected`: Initial agent choice
- `agent_switched`: Agent switching behavior  
- `message_processed`: Successful AI interactions
- `message_error`: Error occurrences
- `conversation_reset`: History clearing
- `stats_viewed`: User engagement with statistics
- `rate_limited`: Usage limit tracking

### Generate Analytics Reports
```bash
# Generate comprehensive usage report
uv run python scripts/analytics_report.py
```

## 🎯 Next Steps After Deployment

1. **Monitor Logs**: Check for any production issues
2. **Test All Features**: Verify /start, agent selection, conversations, /stats
3. **Performance Monitoring**: Watch response times and error rates
4. **Analytics Review**: Use analytics_report.py to track usage patterns
5. **User Feedback**: Gather feedback on bot performance

## 🔧 Environment Variables Required

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 🎉 Your Bot is Production Ready!

All production features have been implemented and tested. Your Telegram AI bot is now ready for deployment to serve users with:

- 🤖 **Two AI Personalities**: Product Manager & VC/Angel Investor
- 🧠 **Real-time AI**: Powered by Perplexity Sonar Pro
- 💾 **Persistent Conversations**: Stored in Supabase
- 🛡️ **Rate Limiting**: Fair usage protection
- 🔧 **Error Handling**: Graceful failure recovery
- 📊 **User Statistics**: Usage tracking and analytics
