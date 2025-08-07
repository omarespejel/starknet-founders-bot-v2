# Webhook Deployment Guide

## 🚨 Fixing "Conflict: terminated by other getUpdates request"

This error occurs when multiple bot instances try to receive updates simultaneously. Here's how to fix it:

## 🛠️ Solution: Switch to Webhook Mode for Production

### 1. **Environment Variables on Render**

Add these environment variables in your Render dashboard:

```bash
WEBHOOK_URL=https://your-app-name.onrender.com
PORT=10000  # Render automatically sets this
TELEGRAM_BOT_TOKEN=your-bot-token
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_KEY=your-supabase-key
OPENROUTER_API_KEY=your-openrouter-key
```

### 2. **How the New System Works**

- **Development (Local)**: Uses polling mode (`run_polling`)
- **Production (Render)**: Uses webhook mode with FastAPI server

The `main.py` automatically detects the environment:
- If `PORT` env var exists → Production webhook mode
- If no `PORT` env var → Development polling mode

### 3. **Webhook Endpoints**

Your deployed bot will have these endpoints:

- `GET /` - Health check
- `GET /health` - Health monitoring
- `POST /webhook` - Telegram webhook receiver

### 4. **Deployment Process**

1. **Update dependencies**: Already done ✅
2. **Set environment variables**: Add `WEBHOOK_URL` on Render
3. **Deploy**: Push your changes to trigger deployment
4. **Verify**: Check `/health` endpoint works

### 5. **Troubleshooting**

If you still get conflicts:

```bash
# Clear any existing webhooks
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook"

# Stop any local bot instances
# Kill any running python processes with your bot
```

### 6. **Monitoring**

Check logs for these success messages:
```
INFO - Starting webhook server on port 10000
INFO - Webhook set to https://your-app.onrender.com/webhook
```

### 7. **Local Development**

For local development, ensure no `PORT` environment variable is set:
```bash
unset PORT  # This ensures polling mode
python main.py
```

## ✅ Benefits of Webhook Mode

1. **No Conflicts**: Only one webhook can be set per bot
2. **Better Performance**: No constant polling
3. **Production Ready**: Scales with your server
4. **Real-time**: Instant message delivery
5. **Monitoring**: Health check endpoints for uptime monitoring

## 🔧 Quick Fix Commands

If you need to quickly clear conflicts:

```bash
# Delete webhook (allows polling again)
curl -X POST "https://api.telegram.org/bot8098805942:AAHV0twoa_Y_vJojKIx9CtqXPTC4z07n0Q8/deleteWebhook"

# Check current webhook status
curl "https://api.telegram.org/bot8098805942:AAHV0twoa_Y_vJojKIx9CtqXPTC4z07n0Q8/getWebhookInfo"
```
