"""Test script with a real, working PR."""

import asyncio
from reviewer.config import config
from reviewer.graph import run_review

async def main():
    print("🧪 Testing with a real GitHub PR\n")
    
    # Validate config first
    try:
        config.validate()
        print("✅ Configuration valid\n")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease update your .env file with:")
        print("  GITHUB_TOKEN=your_token")
        print("  GROQ_API_KEY=your_key")
        return
    
    # Use a small, real PR from a popular repo
    # This is a merged PR from the LangChain repository
    owner = "langchain-ai"
    repo = "langchain"
    pr_number = 15000  # Small documentation fix
    pr_url = f"https://github.com/{owner}/{repo}/pull/{pr_number}"
    
    print(f"Testing on: {pr_url}")
    print("This is a DRY-RUN - will NOT post to GitHub\n")
    print("=" * 80 + "\n")
    
    try:
        await run_review(owner, repo, pr_number, pr_url, should_post=False)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
