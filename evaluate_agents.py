"""Standalone Agent Evaluation Script

Run this to test agent accuracy without pytest.
Generates detailed reports and saves results.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from tests.test_agent_accuracy import TEST_CASES, AgentEvaluator
from reviewer.agents.bug_agent import bug_agent
from reviewer.agents.security_agent import security_agent
from reviewer.agents.style_agent import style_agent
from reviewer.state import ReviewState


async def evaluate_agents():
    """Run comprehensive agent evaluation."""
    
    print("="*80)
    print("AGENTIC CODE REVIEWER - AGENT ACCURACY EVALUATION")
    print("="*80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Cases: {len(TEST_CASES)}")
    print(f"Agents: Bug Agent, Security Agent, Style Agent")
    print("\n" + "="*80 + "\n")
    
    evaluator = AgentEvaluator()
    detailed_results = []
    
    for test_case in TEST_CASES:
        print(f"📋 Test Case {test_case['id']}: {test_case['description']}")
        print("-" * 80)
        
        # Create mock state
        state = ReviewState(
            owner="test",
            repo="test",
            pr_number=test_case['id'],
            pr_url=f"https://test.com/pull/{test_case['id']}",
            pr_title=test_case['description'],
            pr_body="Test case for agent evaluation",
            pr_author="evaluator",
            files=[],
            full_diff=test_case['diff'],
            file_diffs={},
            bug_findings=[],
            security_findings=[],
            style_findings=[],
            final_review="",
            summary="",
            should_post=False,
            error=None
        )
        
        test_result = {
            "id": test_case['id'],
            "description": test_case['description'],
            "agents": {}
        }
        
        # Test Bug Agent
        print("\n  🐛 Bug Agent Analysis:")
        try:
            bug_result = await bug_agent(state)
            bug_findings = bug_result.get("bug_findings", [])
            expected_bug = test_case['expected']['bug']
            
            bug_eval = evaluator.evaluate_findings("bug_agent", bug_findings, expected_bug)
            
            print(f"     Predicted: {len(bug_findings)} issue(s)")
            print(f"     Expected:  {len(expected_bug)} issue(s)")
            print(f"     TP: {bug_eval['true_positives']}, FP: {bug_eval['false_positives']}, FN: {bug_eval['false_negatives']}")
            
            if bug_findings:
                for finding in bug_findings:
                    print(f"       - {finding.get('title', 'Unknown')}")
            
            test_result["agents"]["bug_agent"] = {
                "found": len(bug_findings),
                "expected": len(expected_bug),
                "findings": [f.get("title") for f in bug_findings],
                "metrics": bug_eval
            }
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
            test_result["agents"]["bug_agent"] = {"error": str(e)}
        
        # Test Security Agent
        print("\n  🔒 Security Agent Analysis:")
        try:
            sec_result = await security_agent(state)
            sec_findings = sec_result.get("security_findings", [])
            expected_sec = test_case['expected']['security']
            
            sec_eval = evaluator.evaluate_findings("security_agent", sec_findings, expected_sec)
            
            print(f"     Predicted: {len(sec_findings)} issue(s)")
            print(f"     Expected:  {len(expected_sec)} issue(s)")
            print(f"     TP: {sec_eval['true_positives']}, FP: {sec_eval['false_positives']}, FN: {sec_eval['false_negatives']}")
            
            if sec_findings:
                for finding in sec_findings:
                    print(f"       - {finding.get('title', 'Unknown')}")
            
            test_result["agents"]["security_agent"] = {
                "found": len(sec_findings),
                "expected": len(expected_sec),
                "findings": [f.get("title") for f in sec_findings],
                "metrics": sec_eval
            }
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
            test_result["agents"]["security_agent"] = {"error": str(e)}
        
        # Test Style Agent
        print("\n  ✨ Style Agent Analysis:")
        try:
            style_result = await style_agent(state)
            style_findings = style_result.get("style_findings", [])
            expected_style = test_case['expected']['style']
            
            style_eval = evaluator.evaluate_findings("style_agent", style_findings, expected_style)
            
            print(f"     Predicted: {len(style_findings)} issue(s)")
            print(f"     Expected:  {len(expected_style)} issue(s)")
            print(f"     TP: {style_eval['true_positives']}, FP: {style_eval['false_positives']}, FN: {style_eval['false_negatives']}")
            
            if style_findings:
                for finding in style_findings:
                    print(f"       - {finding.get('title', 'Unknown')}")
            
            test_result["agents"]["style_agent"] = {
                "found": len(style_findings),
                "expected": len(expected_style),
                "findings": [f.get("title") for f in style_findings],
                "metrics": style_eval
            }
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
            test_result["agents"]["style_agent"] = {"error": str(e)}
        
        detailed_results.append(test_result)
        print("\n" + "="*80 + "\n")
    
    # Print final report
    evaluator.print_report()
    
    # Calculate and save metrics
    metrics = evaluator.calculate_metrics()
    
    # Save results
    results_dir = Path("evaluation_results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save summary metrics
    metrics_file = results_dir / f"metrics_{timestamp}.json"
    metrics_file.write_text(json.dumps(metrics, indent=2))
    print(f"📊 Metrics saved to: {metrics_file}")
    
    # Save detailed results
    details_file = results_dir / f"detailed_results_{timestamp}.json"
    details_file.write_text(json.dumps(detailed_results, indent=2))
    print(f"📋 Detailed results saved to: {details_file}")
    
    # Save human-readable report
    report_file = results_dir / f"report_{timestamp}.txt"
    with open(report_file, "w") as f:
        f.write("="*80 + "\n")
        f.write("AGENT ACCURACY EVALUATION REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Test Cases: {len(TEST_CASES)}\n\n")
        
        for agent_name, m in metrics.items():
            f.write(f"\n{agent_name.replace('_', ' ').title()}\n")
            f.write("-" * 40 + "\n")
            
            if agent_name == "synthesizer":
                f.write(f"Accuracy:    {m['accuracy']:.2f}%\n")
                f.write(f"Tests Run:   {m['tests_run']}\n")
            else:
                f.write(f"Accuracy:         {m['accuracy']:.2f}%\n")
                f.write(f"Precision:        {m['precision']:.2f}%\n")
                f.write(f"Recall:           {m['recall']:.2f}%\n")
                f.write(f"F1-Score:         {m['f1_score']:.2f}%\n")
                f.write(f"Hallucination:    {m['hallucination_rate']:.2f}%\n")
                f.write(f"\n")
                f.write(f"True Positives:   {m['true_positives']}\n")
                f.write(f"False Positives:  {m['false_positives']}\n")
                f.write(f"False Negatives:  {m['false_negatives']}\n")
                f.write(f"Tests Run:        {m['tests_run']}\n")
        
        avg_accuracy = sum(m.get("accuracy", 0) for m in metrics.values()) / len(metrics)
        f.write(f"\n{'='*80}\n")
        f.write(f"OVERALL AVERAGE ACCURACY: {avg_accuracy:.2f}%\n")
        f.write(f"{'='*80}\n")
    
    print(f"📄 Report saved to: {report_file}\n")
    
    # Print recommendations
    print("="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    for agent_name, m in metrics.items():
        if agent_name == "synthesizer":
            continue
            
        print(f"\n{agent_name.replace('_', ' ').title()}:")
        
        if m['accuracy'] < 70:
            print(f"  ⚠️  LOW ACCURACY ({m['accuracy']:.0f}%) - Consider:")
            print(f"      - Improving prompts in reviewer/prompts/{agent_name.replace('_agent', '')}.md")
            print(f"      - Adding more examples to the prompt")
            print(f"      - Using a more powerful model")
        elif m['accuracy'] < 85:
            print(f"  ⚡ MODERATE ACCURACY ({m['accuracy']:.0f}%) - Room for improvement")
        else:
            print(f"  ✅ GOOD ACCURACY ({m['accuracy']:.0f}%)")
        
        if m['hallucination_rate'] > 30:
            print(f"  ⚠️  HIGH HALLUCINATION RATE ({m['hallucination_rate']:.0f}%)")
            print(f"      - Agent is flagging too many false positives")
            print(f"      - Consider making prompts more conservative")
        
        if m['recall'] < 70:
            print(f"  ⚠️  LOW RECALL ({m['recall']:.0f}%)")
            print(f"      - Agent is missing real issues")
            print(f"      - Consider making prompts more comprehensive")
    
    print("\n" + "="*80 + "\n")
    
    return metrics


if __name__ == "__main__":
    print("\n🚀 Starting Agent Evaluation...\n")
    metrics = asyncio.run(evaluate_agents())
    print("✅ Evaluation Complete!\n")
