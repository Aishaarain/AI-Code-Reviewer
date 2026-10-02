"""Demo script showing how to use the agentic code reviewer programmatically."""

import asyncio
from reviewer.graph import run_review


async def main():
    """Run a demo review on a public PR."""
    # Example: Review a small PR from a public repo
    # Replace with any public PR you want to test
    
    owner = "octocat"
    repo = "Hello-World"
    pr_number = 1
    pr_url = f"https://github.com/{owner}/{repo}/pull/{pr_number}"
    
    print("This is a demo of the agentic code reviewer.")
    print(f"Testing with: {pr_url}\n")
    
    # Run in dry-run mode (won't post to GitHub)
    await run_review(owner, repo, pr_number, pr_url, should_post=False)


if __name__ == "__main__":
    asyncio.run(main())
