# """Agent Accuracy Testing Framework

# Tests each agent individually and measures:
# - Accuracy
# - Precision
# - Recall
# - F1-score
# - Hallucination rate
# """

# import asyncio
# import json
# from pathlib import Path
# from typing import List, Dict

# try:
#     import pytest
#     PYTEST_AVAILABLE = True
# except ImportError:
#     PYTEST_AVAILABLE = False
#     # Create a dummy pytest.mark.asyncio decorator
#     class DummyPytest:
#         class mark:
#             @staticmethod
#             def asyncio(func):
#                 return func
#     pytest = DummyPytest()

# from reviewer.agents.bug_agent import bug_agent
# from reviewer.agents.security_agent import security_agent
# from reviewer.agents.style_agent import style_agent
# from reviewer.agents.synthesizer import synthesizer_agent
# from reviewer.state import ReviewState


# class AgentEvaluator:
#     """Evaluates agent performance against ground truth."""
    
#     def __init__(self):
#         self.results = {
#             "bug_agent": {"correct": 0, "total": 0, "tp": 0, "fp": 0, "fn": 0, "tn": 0},
#             "security_agent": {"correct": 0, "total": 0, "tp": 0, "fp": 0, "fn": 0, "tn": 0},
#             "style_agent": {"correct": 0, "total": 0, "tp": 0, "fp": 0, "fn": 0, "tn": 0},
#             "synthesizer": {"correct": 0, "total": 0}
#         }
    
#     def evaluate_findings(self, agent_name: str, predicted: List[Dict], expected: List[Dict]) -> Dict:
#         """Evaluate agent findings against ground truth.
        
#         Args:
#             agent_name: Name of the agent
#             predicted: Findings from the agent
#             expected: Ground truth findings
            
#         Returns:
#             Evaluation metrics
#         """
#         stats = self.results[agent_name]
#         stats["total"] += 1
        
#         # Extract issue titles/types for comparison
#         predicted_issues = set(f.get("title", "") for f in predicted)
#         expected_issues = set(e.get("title", "") for e in expected)
        
#         # True Positives: Issues correctly identified
#         tp = len(predicted_issues & expected_issues)
        
#         # False Positives: Issues incorrectly flagged
#         fp = len(predicted_issues - expected_issues)
        
#         # False Negatives: Issues missed
#         fn = len(expected_issues - predicted_issues)
        
#         # True Negatives: Correctly identified no issue (approximation)
#         tn = 0 if (predicted_issues or expected_issues) else 1
        
#         stats["tp"] += tp
#         stats["fp"] += fp
#         stats["fn"] += fn
#         stats["tn"] += tn
        
#         # Count as correct if exact match or close enough
#         if predicted_issues == expected_issues or (tp > 0 and fp == 0 and fn == 0):
#             stats["correct"] += 1
        
#         return {
#             "true_positives": tp,
#             "false_positives": fp,
#             "false_negatives": fn,
#             "true_negatives": tn
#         }
    
#     def calculate_metrics(self) -> Dict:
#         """Calculate accuracy, precision, recall, F1 for all agents."""
#         metrics = {}
        
#         for agent_name, stats in self.results.items():
#             if agent_name == "synthesizer":
#                 # Synthesizer uses simple accuracy
#                 accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
#                 metrics[agent_name] = {
#                     "accuracy": round(accuracy, 2),
#                     "tests_run": stats["total"]
#                 }
#             else:
#                 tp = stats["tp"]
#                 fp = stats["fp"]
#                 fn = stats["fn"]
#                 tn = stats["tn"]
#                 total = stats["total"]
                
#                 # Accuracy: (TP + TN) / Total
#                 accuracy = (stats["correct"] / total * 100) if total > 0 else 0
                
#                 # Precision: TP / (TP + FP)
#                 precision = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0
                
#                 # Recall: TP / (TP + FN)
#                 recall = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0
                
#                 # F1-score: 2 * (Precision * Recall) / (Precision + Recall)
#                 f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
                
#                 # Hallucination rate: FP / (TP + FP)
#                 hallucination_rate = (fp / (tp + fp) * 100) if (tp + fp) > 0 else 0
                
#                 metrics[agent_name] = {
#                     "accuracy": round(accuracy, 2),
#                     "precision": round(precision, 2),
#                     "recall": round(recall, 2),
#                     "f1_score": round(f1, 2),
#                     "hallucination_rate": round(hallucination_rate, 2),
#                     "true_positives": tp,
#                     "false_positives": fp,
#                     "false_negatives": fn,
#                     "true_negatives": tn,
#                     "tests_run": total
#                 }
        
#         return metrics
    
#     def print_report(self):
#         """Print a formatted evaluation report."""
#         metrics = self.calculate_metrics()
        
#         print("\n" + "="*80)
#         print("AGENT ACCURACY EVALUATION REPORT")
#         print("="*80 + "\n")
        
#         for agent_name, m in metrics.items():
#             print(f"🤖 {agent_name.replace('_', ' ').title()}")
#             print("-" * 40)
            
#             if agent_name == "synthesizer":
#                 print(f"  Accuracy:    {m['accuracy']:.2f}%")
#                 print(f"  Tests Run:   {m['tests_run']}")
#             else:
#                 print(f"  Accuracy:         {m['accuracy']:.2f}%")
#                 print(f"  Precision:        {m['precision']:.2f}%")
#                 print(f"  Recall:           {m['recall']:.2f}%")
#                 print(f"  F1-Score:         {m['f1_score']:.2f}%")
#                 print(f"  Hallucination:    {m['hallucination_rate']:.2f}%")
#                 print(f"")
#                 print(f"  True Positives:   {m['true_positives']}")
#                 print(f"  False Positives:  {m['false_positives']}")
#                 print(f"  False Negatives:  {m['false_negatives']}")
#                 print(f"  Tests Run:        {m['tests_run']}")
            
#             print()
        
#         # Overall summary
#         avg_accuracy = sum(m.get("accuracy", 0) for m in metrics.values()) / len(metrics)
#         print("="*80)
#         print(f"OVERALL AVERAGE ACCURACY: {avg_accuracy:.2f}%")
#         print("="*80 + "\n")


# # Test dataset with ground truth
# TEST_CASES = [
#     {
#         "id": 1,
#         "description": "SQL Injection vulnerability",
#         "diff": """diff --git a/database.py b/database.py
# +def get_user(username):
# +    query = f"SELECT * FROM users WHERE username = '{username}'"
# +    return db.execute(query)
# """,
#         "expected": {
#             "bug": [],
#             "security": [
#                {
#     "issue_id": "sql_injection",
#     "category": "security",
#     "severity": "critical",
#     "title": "SQL Injection vulnerability",
#     "file": "database.py"
# }
#             ],
#             "style": []
#         }
#     },
#     {
#         "id": 2,
#         "description": "Division by zero bug",
#         "diff": """diff --git a/math_utils.py b/math_utils.py
# +def calculate_average(total, count):
# +    return total / count
# """,
#         "expected": {
#             "bug": [
#                 {
#                     "category": "bug",
#                     "severity": "high",
#                     "title": "Division by zero not handled",
#                     "file": "math_utils.py"
#                 }
#             ],
#             "security": [],
#             "style": []
#         }
#     },
#     {
#         "id": 3,
#         "description": "Poor code style - deeply nested",
#         "diff": """diff --git a/validator.py b/validator.py
# +def validate(x, y, z):
# +    if x > 0:
# +        if y > 0:
# +            if z > 0:
# +                return True
# +    return False
# """,
#         "expected": {
#             "bug": [],
#             "security": [],
#             "style": [
#                 {
#                     "category": "style",
#                     "severity": "medium",
#                     "title": "Deeply nested conditionals",
#                     "file": "validator.py"
#                 }
#             ]
#         }
#     },
#     {
#         "id": 4,
#         "description": "Clean code - no issues",
#         "diff": """diff --git a/helpers.py b/helpers.py
# +def add(a: int, b: int) -> int:
# +    \"\"\"Add two numbers.\"\"\"
# +    return a + b
# """,
#         "expected": {
#             "bug": [],
#             "security": [],
#             "style": []
#         }
#     },
#     {
#         "id": 5,
#         "description": "Multiple issues",
#         "diff": """diff --git a/api.py b/api.py
# +def process_request(user_input):
# +    # Execute user input directly (security issue)
# +    result = eval(user_input)
# +    
# +    # No error handling (bug)
# +    data = fetch_data()
# +    value = data['key']
# +    
# +    # Magic number (style)
# +    if value > 42:
# +        return result
# """,
#         "expected": {
#             "bug": [
#                 {
#                     "category": "bug",
#                     "severity": "high",
#                     "title": "Missing error handling",
#                     "file": "api.py"
#                 }
#             ],
#             "security": [
#                 {
#                     "category": "security",
#                     "severity": "critical",
#                     "title": "Code injection via eval",
#                     "file": "api.py"
#                 }
#             ],
#             "style": [
#                 {
#                     "category": "style",
#                     "severity": "low",
#                     "title": "Magic number without explanation",
#                     "file": "api.py"
#                 }
#             ]
#         }
#     }
# ]


# @pytest.mark.asyncio
# async def test_agent_accuracy():
#     """Run accuracy tests on all agents."""
#     evaluator = AgentEvaluator()
    
#     print("\n🧪 Running Agent Accuracy Tests...\n")
    
#     for test_case in TEST_CASES:
#         print(f"Test Case {test_case['id']}: {test_case['description']}")
        
#         # Create mock state
#         state = ReviewState(
#             owner="test",
#             repo="test",
#             pr_number=1,
#             pr_url="https://test.com",
#             pr_title=test_case['description'],
#             pr_body="",
#             pr_author="test",
#             files=[],
#             full_diff=test_case['diff'],
#             file_diffs={},
#             bug_findings=[],
#             security_findings=[],
#             style_findings=[],
#             final_review="",
#             summary="",
#             should_post=False,
#             error=None
#         )
        
#         # Test Bug Agent
#         print("  🐛 Testing Bug Agent...")
#         bug_result = await bug_agent(state)
#         bug_findings = bug_result.get("bug_findings", [])
#         evaluator.evaluate_findings("bug_agent", bug_findings, test_case['expected']['bug'])
#         print(f"     Found {len(bug_findings)} issue(s), Expected {len(test_case['expected']['bug'])}")
        
#         # Test Security Agent
#         print("  🔒 Testing Security Agent...")
#         sec_result = await security_agent(state)
#         sec_findings = sec_result.get("security_findings", [])
#         evaluator.evaluate_findings("security_agent", sec_findings, test_case['expected']['security'])
#         print(f"     Found {len(sec_findings)} issue(s), Expected {len(test_case['expected']['security'])}")
        
#         # Test Style Agent
#         print("  ✨ Testing Style Agent...")
#         style_result = await style_agent(state)
#         style_findings = style_result.get("style_findings", [])
#         evaluator.evaluate_findings("style_agent", style_findings, test_case['expected']['style'])
#         print(f"     Found {len(style_findings)} issue(s), Expected {len(test_case['expected']['style'])}")
        
#         print()
    
#     # Print final report
#     evaluator.print_report()
    
#     # Save results to file
#     metrics = evaluator.calculate_metrics()
#     results_file = Path("tests/agent_accuracy_results.json")
#     results_file.write_text(json.dumps(metrics, indent=2))
#     print(f"📊 Results saved to: {results_file}\n")
    
#     # Assert minimum acceptable accuracy
#     for agent_name, m in metrics.items():
#         accuracy = m.get("accuracy", 0)
#         assert accuracy >= 50, f"{agent_name} accuracy ({accuracy}%) below 50% threshold"


# if __name__ == "__main__":
#     # Run tests directly
#     asyncio.run(test_agent_accuracy())



"""Agent Accuracy Testing Framework

Scores each review agent against ground truth, using stable issue_ids.

Finding level (every predicted/expected finding is one item):
    Precision          = TP / (TP + FP)
    Recall             = TP / (TP + FN)
    F1                 = harmonic mean of precision and recall
    Hallucination rate = FP / (TP + FP)   (false discovery rate = 100% - precision)

Case level (every test case is one item):
    Exact-match rate   = cases with no false positives and no misses / all cases
    False-alarm rate   = clean cases where the agent reported anything / clean cases
                         (this is the true false-positive rate)

A predicted finding is a true positive when its issue_id matches an expected
finding (or one of its accepted alternatives) in the same file. Matching is
one-to-one, and predictions are de-duplicated by (issue_id, file) first.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

    class DummyPytest:
        class mark:
            @staticmethod
            def asyncio(func):
                return func
    pytest = DummyPytest()

from agent_eval_dataset import TEST_CASES

AGENT_KEYS = ("bug", "security", "style")
MIN_F1 = 50.0  # percent; raise this as the prompts improve


def _basename(path) -> str:
    return Path(str(path or "")).name.lower()


def _dedupe(findings: List[Dict]) -> List[Dict]:
    seen, unique = set(), []
    for finding in findings:
        key = (finding.get("issue_id", ""), _basename(finding.get("file")))
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    return unique


def match_findings(predicted: List[Dict], expected: List[Dict]):
    """One-to-one matching on issue_id (+ file).

    Returns (true_positives, false_positives, missed) where the last two are lists
    of findings.
    """
    unmatched = _dedupe(predicted)
    tp, missed = 0, []

    for exp in expected:
        accepted = {exp["issue_id"], *exp.get("accept", [])}
        hit = next(
            (
                p for p in unmatched
                if p.get("issue_id") in accepted
                and (not exp.get("file") or _basename(p.get("file")) == _basename(exp["file"]))
            ),
            None,
        )
        if hit is None:
            missed.append(exp)
        else:
            unmatched.remove(hit)
            tp += 1

    return tp, unmatched, missed


class AgentEvaluator:
    """Accumulates per-agent results and computes consistent metrics."""

    def __init__(self):
        self.results = {
            key: {
                "tp": 0, "fp": 0, "fn": 0,
                "cases": 0, "exact": 0,
                "clean_cases": 0, "false_alarms": 0,
                "failures": [],
            }
            for key in AGENT_KEYS
        }

    def evaluate(self, agent_key: str, case_id: str, predicted: List[Dict], expected: List[Dict]) -> Dict:
        stats = self.results[agent_key]
        tp, false_positives, missed = match_findings(predicted, expected)
        fp, fn = len(false_positives), len(missed)

        stats["tp"] += tp
        stats["fp"] += fp
        stats["fn"] += fn
        stats["cases"] += 1

        if not expected:
            stats["clean_cases"] += 1
            if predicted:
                stats["false_alarms"] += 1

        exact = fp == 0 and fn == 0
        if exact:
            stats["exact"] += 1
        else:
            stats["failures"].append({
                "case": case_id,
                "false_positives": [f.get("issue_id") for f in false_positives],
                "missed": [m["issue_id"] for m in missed],
            })

        return {"tp": tp, "fp": fp, "fn": fn, "exact": exact,
                "false_positives": [f.get("issue_id") for f in false_positives],
                "missed": [m["issue_id"] for m in missed]}

    @staticmethod
    def _pct(numerator: float, denominator: float) -> float:
        return round(numerator / denominator * 100, 2) if denominator else 0.0

    def calculate_metrics(self) -> Dict:
        metrics = {}
        for key, s in self.results.items():
            precision = self._pct(s["tp"], s["tp"] + s["fp"])
            recall = self._pct(s["tp"], s["tp"] + s["fn"])
            f1 = round(2 * precision * recall / (precision + recall), 2) if (precision + recall) else 0.0
            metrics[key] = {
                "finding_level": {
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "hallucination_rate": self._pct(s["fp"], s["tp"] + s["fp"]),
                    "true_positives": s["tp"],
                    "false_positives": s["fp"],
                    "false_negatives": s["fn"],
                },
                "case_level": {
                    "exact_match_rate": self._pct(s["exact"], s["cases"]),
                    "false_alarm_rate": self._pct(s["false_alarms"], s["clean_cases"]),
                    "cases": s["cases"],
                    "clean_cases": s["clean_cases"],
                },
                "failures": s["failures"],
            }
        return metrics

    def print_report(self):
        metrics = self.calculate_metrics()
        print("\n" + "=" * 80)
        print("AGENT ACCURACY EVALUATION REPORT")
        print("=" * 80)

        for key, m in metrics.items():
            f, c = m["finding_level"], m["case_level"]
            print(f"\n🤖 {key.title()} Agent")
            print("-" * 40)
            print("  Finding level")
            print(f"    Precision:           {f['precision']:.2f}%")
            print(f"    Recall:              {f['recall']:.2f}%")
            print(f"    F1-Score:            {f['f1_score']:.2f}%")
            print(f"    Hallucination rate:  {f['hallucination_rate']:.2f}%  (FP / (TP + FP))")
            print(f"    TP / FP / FN:        {f['true_positives']} / {f['false_positives']} / {f['false_negatives']}")
            print("  Case level")
            print(f"    Exact-match rate:    {c['exact_match_rate']:.2f}%  ({c['cases']} cases)")
            print(f"    False-alarm rate:    {c['false_alarm_rate']:.2f}%  ({c['clean_cases']} clean cases)")
            for failure in m["failures"]:
                print(f"    ✗ {failure['case']}: FP={failure['false_positives']} missed={failure['missed']}")

        avg_f1 = sum(m["finding_level"]["f1_score"] for m in metrics.values()) / len(metrics)
        print("\n" + "=" * 80)
        print(f"AVERAGE F1 ACROSS AGENTS: {avg_f1:.2f}%")
        print("=" * 80 + "\n")


def _make_state(case: Dict):
    from reviewer.state import create_initial_state
    state = create_initial_state("test", "test", 1, "https://github.com/test/test/pull/1")
    state["pr_title"] = case["description"]
    state["full_diff"] = case["diff"]
    return state


def test_evaluator_matching():
    """Sanity-check the scoring logic itself (no LLM calls)."""
    evaluator = AgentEvaluator()
    expected = [{"issue_id": "sql_injection", "file": "database.py", "accept": ["code_injection"]}]

    # Different wording, same issue_id, path prefix ignored -> TP
    result = evaluator.evaluate("security", "t1", [{"issue_id": "sql_injection", "file": "a/database.py"}], expected)
    assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 0)

    # Accepted alternative id -> TP; duplicate of the same issue is collapsed
    result = evaluator.evaluate(
        "security", "t2",
        [{"issue_id": "code_injection", "file": "database.py"}, {"issue_id": "code_injection", "file": "database.py"}],
        expected,
    )
    assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 0)

    # Wrong id -> one FP and one miss
    result = evaluator.evaluate("security", "t3", [{"issue_id": "xss", "file": "database.py"}], expected)
    assert (result["tp"], result["fp"], result["fn"]) == (0, 1, 1)

    # Clean case with a finding -> false alarm
    evaluator.evaluate("security", "t4", [{"issue_id": "xss", "file": "x.py"}], [])
    metrics = evaluator.calculate_metrics()["security"]
    assert metrics["case_level"]["false_alarm_rate"] == 100.0


@pytest.mark.asyncio
async def test_agent_accuracy():
    """Run accuracy tests on all agents."""
    from reviewer.agents.bug_agent import bug_agent
    from reviewer.agents.security_agent import security_agent
    from reviewer.agents.style_agent import style_agent

    agents = {
        "bug": (bug_agent, "bug_findings", "🐛"),
        "security": (security_agent, "security_findings", "🔒"),
        "style": (style_agent, "style_findings", "✨"),
    }

    evaluator = AgentEvaluator()
    print("\n🧪 Running Agent Accuracy Tests...\n")

    for case in TEST_CASES:
        print(f"Case {case['id']} [{case['group']}]: {case['description']}")
        state = _make_state(case)

        # Sequential on purpose: avoids Groq rate-limit errors.
        for key, (agent, result_key, emoji) in agents.items():
            result = await agent(state)
            predicted = result.get(result_key, [])
            outcome = evaluator.evaluate(key, case["id"], predicted, case["expected"][key])
            status = "✅" if outcome["exact"] else "❌"
            detail = "" if outcome["exact"] else f" FP={outcome['false_positives']} missed={outcome['missed']}"
            print(f"  {emoji} {key}: {status}{detail}")
        print()

    evaluator.print_report()

    metrics = evaluator.calculate_metrics()
    results_file = Path(__file__).parent / "agent_accuracy_results.json"
    results_file.write_text(json.dumps(metrics, indent=2))
    print(f"📊 Results saved to: {results_file}\n")

    for key, m in metrics.items():
        f1 = m["finding_level"]["f1_score"]
        assert f1 >= MIN_F1, f"{key} agent F1 ({f1}%) below {MIN_F1}% threshold"


if __name__ == "__main__":
    test_evaluator_matching()
    asyncio.run(test_agent_accuracy())