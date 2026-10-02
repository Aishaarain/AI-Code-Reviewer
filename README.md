# agentic-code-reviewer

Multi-agent pull request reviewer: Python + LangGraph (orchestration) + Groq (LLM) + GitHub API.

## Flow
fetch PR -> [bug agent | security agent | style agent] (parallel) -> synthesizer -> post review

## Two Ways to Use

### 🖥️ Command Line
```bash
py -m reviewer https://github.com/owner/repo/pull/123           # dry-run
py -m reviewer https://github.com/owner/repo/pull/123 --post   # post review
```

### 🌐 Web Interface (NEW!)
```bash
streamlit run app.py
```
Then paste any PR URL in your browser! See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for details.

---

## Setup

1. **Get API Keys:**
   - **GitHub Token**: Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
     - Permissions: Contents (read), Pull requests (read & write)
   - **Groq API Key**: Get from [console.groq.com](https://console.groq.com) (free tier available!)

2. **Install:**
   ```bash
   py -m venv .venv
   .venv\Scripts\activate  # Windows (or source .venv/bin/activate on Mac/Linux)
   pip install -e ".[dev]"
   ```

3. **Configure:**
   - Copy `.env.example` to `.env`
   - Fill in your `GITHUB_TOKEN` and `GROQ_API_KEY`

## Why Groq?
- **Fast**: 500+ tokens/second inference
- **Free tier**: Generous rate limits
- **Great models**: GPT OSS 120B and Llama models available

---

## 🧪 Testing Agent Accuracy

Test how well your agents are performing:

```bash
.venv\Scripts\python.exe run_tests.py
```

This tests each agent (bug, security, style) against known issues and calculates:
- **Accuracy** - Overall correctness
- **Precision** - How often flagged issues are real
- **Recall** - How many real issues are caught
- **F1-Score** - Balance between precision and recall
- **Hallucination Rate** - False positive percentage

Results saved to `evaluation_results/`

**See [TESTING_SUMMARY.md](TESTING_SUMMARY.md) for detailed results and improvement recommendations.**

---

cd C:\Users\aisha\Downloads\agentic-code-reviewer\agentic-code-reviewer
.venv\Scripts\activate
py -m pytest tests/test_agent_accuracy.py -k evaluator_matching
