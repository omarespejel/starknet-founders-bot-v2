"""Test OpenRouter API connection and model availability."""
import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


async def test_openrouter_connection():
    """Test OpenRouter API connection and Sonar Pro model."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ No OPENROUTER_API_KEY found in .env")
        return
    
    try:
        # Initialize OpenRouter client
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        print("✅ OpenRouter client created successfully")
        
        # Test the Sonar Pro model with a simple message
        print("🧪 Testing perplexity/sonar-pro model...")
        
        response = await client.chat.completions.create(
            model="perplexity/sonar-pro",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant."
                },
                {
                    "role": "user", 
                    "content": "Say hello and confirm you're working!"
                }
            ],
            max_tokens=100,
            temperature=0.7,
        )
        
        if response.choices and response.choices[0].message.content:
            print("✅ Model response received!")
            print(f"🤖 Response: {response.choices[0].message.content}")
            print(f"📊 Tokens used: {response.usage.total_tokens if response.usage else 'Unknown'}")
        else:
            print("⚠️  Empty response from model")
            
    except Exception as e:
        print(f"❌ Error testing OpenRouter: {e}")
        
        # Provide specific guidance based on error type
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            print("💡 Tip: Check your OPENROUTER_API_KEY in .env file")
        elif "404" in error_str or "not found" in error_str:
            print("💡 Tip: The model 'perplexity/sonar-pro' might not be available")
            print("   Visit https://openrouter.ai/models to check available models")
        elif "429" in error_str:
            print("💡 Tip: Rate limit reached, wait a moment and try again")


if __name__ == "__main__":
    print("🚀 Testing OpenRouter API connection...")
    print("=" * 50)
    asyncio.run(test_openrouter_connection())
