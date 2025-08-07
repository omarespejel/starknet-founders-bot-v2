"""Generate analytics report from bot usage data."""
import asyncio
import os
from datetime import datetime, timedelta, UTC
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


async def generate_analytics_report():
    """Generate a comprehensive analytics report."""
    try:
        # Initialize Supabase client
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        print("📊 Bot Analytics Report")
        print("=" * 50)
        
        # Get date ranges
        now = datetime.now(UTC)
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Total users
        total_users = supabase.table('bot_analytics')\
            .select('user_id', count='exact')\
            .execute()
        
        unique_users = supabase.table('bot_analytics')\
            .select('user_id')\
            .execute()
        
        unique_user_count = len(set(row['user_id'] for row in unique_users.data))
        
        print(f"👥 Total Users: {unique_user_count}")
        print(f"📈 Total Events: {total_users.count}")
        
        # Activity by time period
        for period_name, period_date in [("24 hours", last_24h), ("7 days", last_7d), ("30 days", last_30d)]:
            events = supabase.table('bot_analytics')\
                .select('*')\
                .gte('created_at', period_date.isoformat())\
                .execute()
            
            users = set(row['user_id'] for row in events.data)
            print(f"📅 Last {period_name}: {len(events.data)} events, {len(users)} users")
        
        # Most popular actions
        print(f"\n🎯 Popular Actions:")
        actions = supabase.table('bot_analytics')\
            .select('action')\
            .execute()
        
        action_counts = {}
        for row in actions.data:
            action = row['action']
            action_counts[action] = action_counts.get(action, 0) + 1
        
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {action}: {count}")
        
        # Agent preferences
        print(f"\n🤖 Agent Preferences:")
        agent_selections = supabase.table('bot_analytics')\
            .select('metadata')\
            .eq('action', 'agent_selected')\
            .execute()
        
        agent_counts = {"pm": 0, "vc": 0}
        for row in agent_selections.data:
            if row['metadata'] and 'agent_type' in row['metadata']:
                agent_type = row['metadata']['agent_type']
                if agent_type in agent_counts:
                    agent_counts[agent_type] += 1
        
        print(f"   🚀 Product Manager: {agent_counts['pm']}")
        print(f"   🦈 VC/Angel: {agent_counts['vc']}")
        
        # Recent errors
        errors = supabase.table('bot_analytics')\
            .select('*')\
            .eq('action', 'message_error')\
            .gte('created_at', last_7d.isoformat())\
            .execute()
        
        print(f"\n⚠️  Errors (last 7 days): {len(errors.data)}")
        
        # Rate limiting
        rate_limits = supabase.table('bot_analytics')\
            .select('*')\
            .eq('action', 'rate_limited')\
            .gte('created_at', last_7d.isoformat())\
            .execute()
        
        print(f"🚫 Rate Limits (last 7 days): {len(rate_limits.data)}")
        
        print(f"\n✅ Report generated successfully!")
        
    except Exception as e:
        print(f"❌ Error generating analytics report: {e}")


if __name__ == "__main__":
    asyncio.run(generate_analytics_report())
