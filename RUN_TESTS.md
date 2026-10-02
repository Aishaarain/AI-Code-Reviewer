# How to Run Agent Accuracy Tests

## Quick Start (Windows)

### Option 1: Simple Python Command (Recommended)
```cmd
.venv\Scripts\python.exe run_tests.py
```

### Option 2: Direct Evaluation Script
```cmd
.venv\Scripts\python.exe evaluate_agents.py
```

### Option 3: With Pytest
```cmd
.venv\Scripts\python.exe -m pytest tests/test_agent_accuracy.py -v
```

## What Gets Tested?

- **Bug Agent** - Tests ability to detect logic errors
- **Security Agent** - Tests ability to detect vulnerabilities  
- **Style Agent** - Tests ability to detect code quality issues

## Test Cases

1. SQL Injection vulnerability
2. Division by zero bug
3. Poor code style (nested conditionals)
4. Clean code (no issues)
5. Multiple issues at once

## Results

After running, you'll find:

- `evaluation_results/metrics_*.json` - Performance metrics
- `evaluation_results/detailed_results_*.json` - Detailed findings
- `evaluation_results/report_*.txt` - Human-readable report

## Understanding Metrics

- **Accuracy** - Overall correctness (%)
- **Precision** - When agent flags something, how often is it right? (%)
- **Recall** - How many real issues did it catch? (%)
- **F1-Score** - Balance between precision and recall
- **Hallucination Rate** - How often does it flag false positives? (%)

## Improving Agents

If scores are low:

1. Edit prompts in `reviewer/prompts/*.md`
2. Add more specific examples
3. Make agents more/less conservative
4. Try a different model in `.env`

## Troubleshooting

### "ModuleNotFoundError: No module named 'pytest'"
```cmd
.venv\Scripts\python.exe -m pip install pytest
```

### "No module named 'reviewer'"
Make sure you're in the project root directory.

### Unicode/Emoji errors on Windows
Use `run_tests.py` which handles encoding properly.

## Adding More Test Cases

Edit `tests/test_agent_accuracy.py` and add to the `TEST_CASES` list:

```python
{
    "id": 6,
    "description": "Your test description",
    "diff": """your git diff here""",
    "expected": {
        "bug": [...],
        "security": [...],
        "style": [...]
    }
}
```
