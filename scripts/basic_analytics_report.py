"""Generate basic analytics report using existing tables only."""
import asyncio
import os
from datetime import datetime, timedelta, UTC
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


async def generate_basic_analytics_report():
    """Generate a basic analytics report using conversations and user_sessions tables."""
    try:
        # Initialize Supabase client
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        print("📊 Basic Bot Analytics Report")
        print("=" * 50)
        print("ℹ️  Using existing tables (conversations, user_sessions)")
        print("   For full analytics, create the bot_analytics table")
        print()
        
        # Get date ranges
        now = datetime.now(UTC)
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Total unique users from conversations
        conversations = supabase.table('conversations')\
            .select('user_id')\
            .execute()
        
        unique_users = set(row['user_id'] for row in conversations.data)
        print(f"👥 Total Unique Users: {len(unique_users)}")
        
        # Total messages
        total_messages = supabase.table('conversations')\
            .select('id', count='exact')\
            .eq('role', 'user')\
            .execute()
        
        print(f"💬 Total User Messages: {total_messages.count}")
        
        # Messages by agent type
        pm_messages = supabase.table('conversations')\
            .select('id', count='exact')\
            .eq('agent_type', 'pm')\
            .eq('role', 'user')\
            .execute()
        
        vc_messages = supabase.table('conversations')\
            .select('id', count='exact')\
            .eq('agent_type', 'vc')\
            .eq('role', 'user')\
            .execute()
        
        print(f"🚀 PM Agent Messages: {pm_messages.count}")
        print(f"🦈 VC Agent Messages: {vc_messages.count}")
        
        # Activity by time period
        print(f"\n📅 Activity by Time Period:")
        for period_name, period_date in [("24 hours", last_24h), ("7 days", last_7d), ("30 days", last_30d)]:
            messages = supabase.table('conversations')\
                .select('user_id')\
                .eq('role', 'user')\
                .gte('created_at', period_date.isoformat())\
                .execute()
            
            active_users = set(row['user_id'] for row in messages.data)
            print(f"   Last {period_name}: {len(messages.data)} messages, {len(active_users)} active users")
        
        # Active sessions
        active_sessions = supabase.table('user_sessions')\
            .select('*')\
            .execute()
        
        print(f"\n👤 Active Sessions: {len(active_sessions.data)}")
        
        # Agent preferences from sessions
        agent_prefs = {"pm": 0, "vc": 0}
        for session in active_sessions.data:
            current_agent = session.get('current_agent', '')
            if current_agent in agent_prefs:
                agent_prefs[current_agent] += 1
        
        print(f"🤖 Current Agent Preferences:")
        print(f"   🚀 Product Manager: {agent_prefs['pm']}")
        print(f"   🦈 VC/Angel: {agent_prefs['vc']}")
        
        # Most active users (top 5)
        user_message_counts = {}
        for row in conversations.data:
            user_id = row['user_id']
            user_message_counts[user_id] = user_message_counts.get(user_id, 0) + 1
        
        top_users = sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print(f"\n🏆 Most Active Users (Top 5):")
        for i, (user_id, count) in enumerate(top_users, 1):
            print(f"   {i}. User {user_id[-8:]}: {count} messages")
        
        # Recent activity
        recent_messages = supabase.table('conversations')\
            .select('*')\
            .eq('role', 'user')\
            .gte('created_at', last_24h.isoformat())\
            .order('created_at', desc=True)\
            .limit(5)\
            .execute()
        
        print(f"\n🕐 Recent Activity (Last 24h):")
        for msg in recent_messages.data:
            created_at = datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00'))
            time_ago = now - created_at
            hours_ago = int(time_ago.total_seconds() / 3600)
            agent_emoji = "🚀" if msg['agent_type'] == 'pm' else "🦈"
            print(f"   {agent_emoji} {hours_ago}h ago: User {msg['user_id'][-8:]} ({msg['agent_type']})")
        
        print(f"\n✅ Basic report generated successfully!")
        print(f"\n💡 To get full analytics:")
        print("1. Run: uv run python scripts/run_migrations.py")
        print("2. Copy the bot_analytics table SQL to your Supabase SQL editor")
        print("3. Execute the SQL to create the analytics table")
        print("4. Run: uv run python scripts/analytics_report.py")
        
    except Exception as e:
        print(f"❌ Error generating basic analytics report: {e}")


if __name__ == "__main__":
    asyncio.run(generate_basic_analytics_report())
