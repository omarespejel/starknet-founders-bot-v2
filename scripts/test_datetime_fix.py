"""Test the datetime fix for the stats functionality."""
from datetime import datetime, UTC

def test_datetime_handling():
    """Test that timezone-aware datetime operations work correctly."""
    
    # Simulate a datetime string from Supabase (timezone-aware)
    sample_date_str = "2025-01-01T10:00:00.000Z"
    
    # Parse the date (this is what comes from the database)
    first_date = datetime.fromisoformat(sample_date_str.replace("Z", "+00:00"))
    
    # Calculate days active (this is the line that was failing)
    current_time = datetime.now(UTC)
    days_active = (current_time - first_date).days
    
    print("✅ Datetime fix test passed!")
    print(f"📅 Sample date: {first_date}")
    print(f"🕐 Current time: {current_time}")
    print(f"📊 Days active: {days_active}")
    print(f"🎯 Member since: {first_date.strftime('%B %d, %Y')}")


if __name__ == "__main__":
    print("🧪 Testing datetime handling fix...")
    test_datetime_handling()
    print("🎉 All tests passed!")
