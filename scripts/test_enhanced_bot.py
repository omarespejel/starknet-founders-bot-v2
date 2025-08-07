"""Test enhanced bot features."""
import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Enable debug logging to see citation processing
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

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
    
    # Test citation parsing
    print("\n" + "="*50 + "\n")
    test_citations = """This is a fact about startups [1] and another insight [2].

Sources:
1. TechCrunch Article - https://techcrunch.com/example
2. Harvard Business Review - https://hbr.org/example"""
    
    print("Citation Test Input:")
    print(repr(test_citations))
    print("\nCitation Test Output:")
    citation_formatted = ai.format_response(test_citations, "pm")
    print(citation_formatted)
    
    # Test direct citation extraction
    print("\n" + "="*30 + "\n")
    print("Direct Citation Extraction Test:")
    extracted = ai.extract_and_format_citations(test_citations)
    print(extracted)
    
    # Test reference cleaning
    print("\n" + "="*30 + "\n")
    test_references = """• **For Users:** There is no guarantee of ownership, ability to contribute to or sustain digital organisms, or assurance that their efforts/creations will last[1][3].
• This is another point with references[2][4][5].
• Single reference here[1]."""
    
    print("Reference Cleaning Test Input:")
    print(test_references)
    print("\nReference Cleaning Test Output:")
    cleaned = ai.clean_references(test_references)
    print(cleaned)

if __name__ == "__main__":
    asyncio.run(test_enhanced_formatting())
