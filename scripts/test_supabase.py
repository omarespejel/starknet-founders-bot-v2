"""Test script for Supabase connection."""

import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


async def test_supabase_connection():
    """Test Supabase connection and basic operations."""
    try:
        # Initialize Supabase client
        supabase = create_client(
            os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY")
        )

        print("✅ Supabase client created successfully")

        # Test a simple query (this will fail if tables don't exist yet)
        try:
            result = supabase.table("conversations").select("*").limit(1).execute()
            print(f"✅ Conversations table query successful: {len(result.data)} rows")
        except Exception as e:
            print(
                f"⚠️  Conversations table query failed (expected if tables don't exist): {e}"
            )

        try:
            result = supabase.table("user_sessions").select("*").limit(1).execute()
            print(f"✅ User sessions table query successful: {len(result.data)} rows")
        except Exception as e:
            print(
                f"⚠️  User sessions table query failed (expected if tables don't exist): {e}"
            )

        print("\n🎯 Supabase connection test completed!")

    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        print("Please check your SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file")


if __name__ == "__main__":
    asyncio.run(test_supabase_connection())
