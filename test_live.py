"""Quick test script to see the reviewer in action."""

import asyncio
from reviewer.config import config
from reviewer.graph import run_review

async def main():
    print("🧪 Testing Agentic Code Reviewer\n")
    
    # Validate config first
    try:
        config.validate()
        print("✅ Configuration valid")
        print(f"   GitHub Token: {config.github_token[:10]}...")
        print(f"   Groq API Key: {config.groq_api_key[:10]}...")
        print(f"   Model: {config.model}\n")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease update your .env file with:")
        print("  GITHUB_TOKEN=your_token")
        print("  GROQ_API_KEY=your_key")
        return
    
    # Test on a small public PR
    # This is a real PR you can use for testing
    owner = "torvalds"
    repo = "linux"
    pr_number = 1  # Use a small, closed PR
    pr_url = f"https://github.com/{owner}/{repo}/pull/{pr_number}"
    
    print(f"Testing on: {pr_url}")
    print("This is a dry-run - will NOT post to GitHub\n")
    print("=" * 80)
    
    try:
        await run_review(owner, repo, pr_number, pr_url, should_post=False)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nCommon issues:")
        print("  - Invalid GitHub token")
        print("  - Invalid Groq API key")
        print("  - PR doesn't exist or is private")
        print("  - Rate limit exceeded")

if __name__ == "__main__":
    asyncio.run(main())
