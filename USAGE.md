# Usage Guide

## Quick Start

### 1. Setup Your Environment

Make sure you have your `.env` file configured:

```bash
GITHUB_TOKEN=ghp_your_github_token_here
GROQ_API_KEY=gsk_your_groq_api_key_here
MODEL=llama-3.3-70b-versatile
```

**Getting API Keys:**
- **GitHub Token**: Settings → Developer settings → Personal access tokens → Fine-grained tokens
  - Permissions: Contents (read), Pull requests (read & write)
- **Groq API Key**: https://console.groq.com/keys (free tier available!)

### 2. Run a Review

**Dry-run mode** (prints to console, doesn't post to GitHub):
```bash
python -m reviewer https://github.com/owner/repo/pull/123
```

**Post mode** (actually posts the review to GitHub):
```bash
python -m reviewer https://github.com/owner/repo/pull/123 --post
```

## What Happens During a Review?

The tool follows this workflow:

```
1. 📥 Fetch PR
   ↓
2. 🔀 Three agents run in parallel:
   ├─ 🐛 Bug Agent (logic errors, edge cases)
   ├─ 🔒 Security Agent (vulnerabilities)
   └─ ✨ Style Agent (code quality)
   ↓
3. 🔄 Synthesizer (combines & prioritizes)
   ↓
4. 📤 Post Review (or print to console)
```

## Available Models

You can use different Groq models by changing the `MODEL` in your `.env`:

- `llama-3.3-70b-versatile` (recommended, best quality)
- `llama3-70b-8192` (fast, good quality)
- `llama3-8b-8192` (fastest, lighter reviews)
- `mixtral-8x7b-32768` (good for large PRs)

Example:
```bash
MODEL=llama3-8b-8192 python -m reviewer <PR_URL>
```

## Testing on Your Own PRs

**Safest way to test:**

1. Create a test repository
2. Create a simple PR with intentional bugs/issues
3. Run the reviewer in dry-run mode first
4. Check the output looks good
5. Try `--post` mode to see it comment on the PR

**Example test PR ideas:**
- Add a function with a division by zero bug
- Include a SQL query with string concatenation
- Write a deeply nested if-else block
- Mix different naming conventions

## Examples

### Review a small PR (dry-run)
```bash
python -m reviewer https://github.com/torvalds/linux/pull/123
```

### Review and post to your own PR
```bash
python -m reviewer https://github.com/yourusername/yourrepo/pull/5 --post
```

### Use a faster model for quick reviews
```bash
MODEL=llama3-8b-8192 python -m reviewer <PR_URL>
```

## Customizing Prompts

The agent prompts are in `reviewer/prompts/`:
- `bug.md` - Bug detection instructions
- `security.md` - Security review instructions
- `style.md` - Code quality instructions
- `synthesizer.md` - Final review synthesis

You can edit these to:
- Add your team's specific coding standards
- Focus on particular frameworks or languages
- Adjust severity thresholds
- Change the review tone

## Programmatic Usage

You can also use the reviewer as a library:

```python
import asyncio
from reviewer.graph import run_review

async def main():
    await run_review(
        owner="octocat",
        repo="Hello-World",
        pr_number=1,
        pr_url="https://github.com/octocat/Hello-World/pull/1",
        should_post=False  # Set to True to post review
    )

asyncio.run(main())
```

## Troubleshooting

**"Configuration error: GROQ_API_KEY not set"**
- Make sure you have a `.env` file in the project root
- Check that it contains `GROQ_API_KEY=your_key`

**"Invalid GitHub PR URL"**
- URL must be in format: `https://github.com/owner/repo/pull/123`
- Make sure it's a pull request, not an issue

**"httpx.HTTPStatusError: 404"**
- PR might not exist or be private
- Your GitHub token might not have access to the repository

**"Rate limit exceeded"**
- GitHub API has rate limits (5000/hour authenticated)
- Groq free tier has limits too (check console.groq.com)
- Wait a few minutes and try again

**Agents returning empty findings**
- This is normal for clean code!
- Try testing on a PR with known issues
- Check that the diff isn't empty

## Tips for Best Results

1. **Test on small PRs first** - Large PRs (>500 lines) may get truncated
2. **Use specific prompts** - Customize the agent prompts for your needs
3. **Review the output** - Always have a human review the AI's suggestions
4. **Iterate on prompts** - The quality depends heavily on the prompts
5. **Monitor costs** - Groq is free but track your usage

## CI/CD Integration

You can run this in GitHub Actions. Example workflow:

```yaml
name: AI Code Review
on: pull_request

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install reviewer
        run: |
          pip install -e .
      - name: Run review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          python -m reviewer ${{ github.event.pull_request.html_url }} --post
```

See `.github/workflows/review.yml` for the full example.
