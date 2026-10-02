"""Command-line interface for the code reviewer."""

import argparse
import asyncio
import sys

from reviewer.config import config
from reviewer.utils import parse_pr_url
from reviewer.graph import run_review


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agentic Code Reviewer - AI-powered PR review with parallel agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (print review to console):
  python -m reviewer https://github.com/owner/repo/pull/123
  
  # Post review to GitHub:
  python -m reviewer https://github.com/owner/repo/pull/123 --post
  
  # Use a different model:
  MODEL=llama3-70b-8192 python -m reviewer <PR_URL>
        """
    )
    
    parser.add_argument(
        "pr_url",
        help="GitHub pull request URL (e.g., https://github.com/owner/repo/pull/123)"
    )
    
    parser.add_argument(
        "--post",
        action="store_true",
        help="Post the review to GitHub (default: dry-run, print to console)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="agentic-code-reviewer 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        print("\nPlease create a .env file with:", file=sys.stderr)
        print("  GITHUB_TOKEN=your_token", file=sys.stderr)
        print("  GROQ_API_KEY=your_key", file=sys.stderr)
        print("  MODEL=llama-3.3-70b-versatile", file=sys.stderr)
        sys.exit(1)
    
    # Parse PR URL
    try:
        owner, repo, pr_number = parse_pr_url(args.pr_url)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run the review
    try:
        asyncio.run(run_review(owner, repo, pr_number, args.pr_url, should_post=args.post))
    except KeyboardInterrupt:
        print("\n\n⚠️  Review interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
