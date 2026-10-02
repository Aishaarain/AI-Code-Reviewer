# """Bug detection agent for code reviews.

# Identifies logic errors, edge cases, and potential bugs in code changes.
# """

# import json
# from pathlib import Path
# from typing import List

# from langchain_core.messages import HumanMessage, SystemMessage

# from reviewer.llm import default_llm
# from reviewer.state import ReviewState, ReviewFinding
# from reviewer.utils import truncate_large_diff


# # Load the bug detection prompt
# PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug.md"
# BUG_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")


# async def bug_agent(state: ReviewState) -> dict:
#     """Analyze code changes for bugs and logic errors.
    
#     Args:
#         state: Current review state with PR data and diffs.
        
#     Returns:
#         Dict with bug_findings key.
#     """
#     print("🐛 Bug Agent: Analyzing for logic errors and edge cases...")
    
#     # Get the diff to analyze
#     full_diff = state.get("full_diff", "")
#     if not full_diff:
#         print("   No diff to analyze")
#         return {"bug_findings": []}
    
#     # Truncate if too large
#     diff_to_analyze = truncate_large_diff(full_diff, max_lines=1000)
    
#     # Prepare the analysis prompt
#     pr_context = f"""
# # Pull Request Information
# **Title:** {state.get('pr_title', 'N/A')}
# **Author:** {state.get('pr_author', 'N/A')}
# **Description:** {state.get('pr_body', 'No description provided')}

# # Files Changed
# {len(state.get('files', []))} files changed

# # Diff to Review
# ```diff
# {diff_to_analyze}
# ```

# Please analyze the above changes for bugs, logic errors, and edge cases.
# Return your findings as a JSON array of objects with this structure:
# [
#   {{
#     "category": "bug",
#     "severity": "critical|high|medium|low",
#     "file": "path/to/file",
#     "line": 42,
#     "title": "Brief issue description",
#     "description": "Detailed explanation",
#     "suggestion": "How to fix"
#   }}
# ]

# If no bugs found, return an empty array: []
# """
    
#     try:
#         # Call the LLM
#         messages = [
#             SystemMessage(content=BUG_PROMPT),
#             HumanMessage(content=pr_context)
#         ]
        
#         response = await default_llm.ainvoke(messages)
        
#         # Parse the response
#         findings = parse_findings(response.content)
        
#         print(f"   Found {len(findings)} potential bug(s)")
#         return {"bug_findings": findings}
        
#     except Exception as e:
#         print(f"   ⚠️  Error in bug agent: {e}")
#         return {"bug_findings": []}


# def parse_findings(response_text: str) -> List[ReviewFinding]:
#     """Parse LLM response into structured findings.
    
#     Args:
#         response_text: Raw text response from LLM.
        
#     Returns:
#         List of ReviewFinding dicts.
#     """
#     try:
#         # Try to extract JSON from the response
#         # LLM might wrap it in markdown code blocks
#         text = response_text.strip()
        
#         # Remove markdown code blocks if present
#         if text.startswith("```json"):
#             text = text[7:]
#         elif text.startswith("```"):
#             text = text[3:]
        
#         if text.endswith("```"):
#             text = text[:-3]
        
#         text = text.strip()
        
#         # Parse JSON
#         findings_data = json.loads(text)
        
#         # Validate structure
#         if not isinstance(findings_data, list):
#             print(f"   ⚠️  Response is not a list, got: {type(findings_data)}")
#             return []
        
#         # Convert to ReviewFinding dicts
#         findings = []
#         for item in findings_data:
#             if isinstance(item, dict):
#                 # Ensure it has required fields
#                 if "category" in item and "title" in item:
#                     findings.append(ReviewFinding(**item))
        
#         return findings
        
#     except json.JSONDecodeError as e:
#         print(f"   ⚠️  Failed to parse JSON response: {e}")
#         print(f"   Response preview: {response_text[:200]}")
#         return []
#     except Exception as e:
#         print(f"   ⚠️  Unexpected error parsing findings: {e}")
#         return []


"""Bug detection agent for code reviews.

Identifies logic errors, edge cases, and potential bugs in code changes.
"""

from pathlib import Path

from reviewer.agents.base import run_agent
from reviewer.state import ReviewState

# Load the bug detection prompt
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug.md"
BUG_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")

BUG_TAXONOMY = {
    "division_by_zero": "Division or modulo where the divisor can be zero",
    "null_dereference": "Attribute access, method call or indexing on a value that can be None/null",
    "missing_key_access": "Reading a dict key, map entry or index that can be absent",
    "off_by_one": "Loop bound or index that is off by one",
    "incorrect_logic": "Wrong operator, swapped arguments, or an inverted/impossible condition",
    "unreachable_code": "Statements after return/raise/break that can never run",
    "resource_leak": "File, socket, connection or lock not released on every path",
    "missing_error_handling": "A failure that is silently ignored or leaves state inconsistent",
    "race_condition": "Shared state modified without synchronisation",
    "type_error": "Operation on incompatible types that raises or gives wrong results",
}

BUG_SEVERITIES = ("critical", "high", "medium", "low")


async def bug_agent(state: ReviewState) -> dict:
    """Analyze code changes for bugs and logic errors.

    Args:
        state: Current review state with PR data and diffs.

    Returns:
        Dict with bug_findings key.
    """
    return await run_agent(
        state=state,
        label="Bug Agent",
        emoji="🐛",
        category="bug",
        result_key="bug_findings",
        system_prompt=BUG_PROMPT,
        taxonomy=BUG_TAXONOMY,
        severities=BUG_SEVERITIES,
        focus="Review the added lines for real bugs, logic errors and edge-case failures.",
        default_severity="medium",
    )