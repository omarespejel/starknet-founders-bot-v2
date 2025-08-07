"""Test enhanced bot features."""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.bot.agents import AIAgent

async def test_enhanced_formatting():
    """Test the new formatting capabilities."""
    ai = AIAgent()
    
    # Test response formatting
    test_content = """
What problem are you solving?
Who is your target user?
Let's talk about Jobs-to-be-Done framework.
Here are some key points:
- First point about growth
- Second point about retention
What's your CAC to LTV ratio?
"""
    
    formatted = ai.format_response(test_content, "pm")
    print("Formatted PM Response:")
    print(formatted)
    print("\n" + "="*50 + "\n")
    
    formatted_vc = ai.format_response(test_content, "vc")
    print("Formatted VC Response:")
    print(formatted_vc)

if __name__ == "__main__":
    asyncio.run(test_enhanced_formatting())
