"""Display SQL migrations that need to be run manually in Supabase."""

import os
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


def check_tables_exist():
    """Check which tables exist in the database."""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        print("🔍 Checking existing tables...")
        
        # Try to query each expected table
        tables_to_check = ['conversations', 'user_sessions', 'bot_analytics']
        existing_tables = []
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                existing_tables.append(table)
                print(f"   ✅ {table} - exists")
            except Exception as e:
                print(f"   ❌ {table} - missing: {str(e)}")
        
        return existing_tables
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return []


def display_migrations():
    """Display SQL migration content for manual execution."""
    try:
        print("\n🚀 Database Migration Setup")
        print("=" * 50)
        
        # Check existing tables
        existing_tables = check_tables_exist()
        
        # Get migrations directory
        migrations_dir = Path(__file__).parent.parent / "migrations"
        
        if not migrations_dir.exists():
            print("❌ Migrations directory not found!")
            return
        
        # Get all SQL files and sort them
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        if not migration_files:
            print("❌ No migration files found!")
            return
        
        print(f"\n📄 Found {len(migration_files)} migration files:")
        
        # Display each migration
        for migration_file in migration_files:
            print(f"\n{'='*60}")
            print(f"📄 {migration_file.name}")
            print(f"{'='*60}")
            
            # Check if this migration is needed
            if migration_file.name == "001_initial_schema.sql":
                needed = not all(table in existing_tables for table in ['conversations', 'user_sessions'])
            elif migration_file.name == "002_analytics_table.sql":
                needed = 'bot_analytics' not in existing_tables
            else:
                needed = True
            
            if needed:
                print("🟡 STATUS: NEEDS TO BE RUN")
            else:
                print("🟢 STATUS: ALREADY APPLIED")
            
            print("\n📝 SQL Content:")
            print("-" * 40)
            
            # Read and display the SQL content
            sql_content = migration_file.read_text()
            print(sql_content)
            
            print("-" * 40)
        
        print(f"\n📋 INSTRUCTIONS:")
        print("1. Open your Supabase dashboard")
        print("2. Go to SQL Editor")
        print("3. Copy and paste each migration marked as 'NEEDS TO BE RUN'")
        print("4. Execute the SQL in order (001, 002, etc.)")
        print("5. Run the analytics report again")
        
        if 'bot_analytics' not in existing_tables:
            print(f"\n⚠️  IMPORTANT: The bot_analytics table is missing!")
            print("   This is why your analytics report is failing.")
            print("   Please run migration 002_analytics_table.sql")
        
    except Exception as e:
        print(f"❌ Error displaying migrations: {e}")


if __name__ == "__main__":
    display_migrations()
