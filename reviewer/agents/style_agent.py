# """Code style and maintainability agent for code reviews.

# Identifies style issues, readability problems, and maintainability concerns.
# """

# import json
# from pathlib import Path
# from typing import List

# from langchain_core.messages import HumanMessage, SystemMessage

# from reviewer.llm import default_llm
# from reviewer.state import ReviewState, ReviewFinding
# from reviewer.utils import truncate_large_diff


# # Load the style review prompt
# PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "style.md"
# STYLE_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")


# async def style_agent(state: ReviewState) -> dict:
#     """Analyze code changes for style and maintainability issues.
    
#     Args:
#         state: Current review state with PR data and diffs.
        
#     Returns:
#         Dict with style_findings key.
#     """
#     print("✨ Style Agent: Analyzing for code quality and maintainability...")
    
#     # Get the diff to analyze
#     full_diff = state.get("full_diff", "")
#     if not full_diff:
#         print("   No diff to analyze")
#         return {"style_findings": []}
    
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

# Please analyze the above changes for code style, readability, and maintainability issues.
# Return your findings as a JSON array of objects with this structure:
# [
#   {{
#     "category": "style",
#     "severity": "high|medium|low|info",
#     "file": "path/to/file",
#     "line": 42,
#     "title": "Brief style issue description",
#     "description": "Detailed explanation of the issue",
#     "suggestion": "How to improve"
#   }}
# ]

# If no style issues found, return an empty array: []
# """
    
#     try:
#         # Call the LLM
#         messages = [
#             SystemMessage(content=STYLE_PROMPT),
#             HumanMessage(content=pr_context)
#         ]
        
#         response = await default_llm.ainvoke(messages)
        
#         # Parse the response
#         findings = parse_findings(response.content)
        
#         print(f"   Found {len(findings)} style/maintainability issue(s)")
#         return {"style_findings": findings}
        
#     except Exception as e:
#         print(f"   ⚠️  Error in style agent: {e}")
#         return {"style_findings": []}


# def parse_findings(response_text: str) -> List[ReviewFinding]:
#     """Parse LLM response into structured findings.
    
#     Args:
#         response_text: Raw text response from LLM.
        
#     Returns:
#         List of ReviewFinding dicts.
#     """
#     try:
#         # Try to extract JSON from the response
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

"""Code style and maintainability agent for code reviews.

Identifies style issues, readability problems, and maintainability concerns.
"""

from pathlib import Path

from reviewer.agents.base import run_agent
from reviewer.state import ReviewState

# Load the style review prompt
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "style.md"
STYLE_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")

STYLE_TAXONOMY = {
    "deep_nesting": "Three or more levels of nested conditionals/loops that guard clauses would flatten",
    "magic_number": "Unexplained numeric or string literal that encodes a business rule or threshold",
    "code_duplication": "The same block of logic repeated with only the values changed",
    "poor_naming": "Single-letter, meaningless or misleading names for functions, parameters or variables",
    "overly_long_function": "Function that does several unrelated things and is hard to follow",
    "overly_complex_logic": "Convoluted expression or control flow that can be written far more simply",
    "misleading_comment": "Comment that contradicts or misdescribes the code next to it",
}

STYLE_SEVERITIES = ("high", "medium", "low", "info")


async def style_agent(state: ReviewState) -> dict:
    """Analyze code changes for style and maintainability issues.

    Args:
        state: Current review state with PR data and diffs.

    Returns:
        Dict with style_findings key.
    """
    return await run_agent(
        state=state,
        label="Style Agent",
        emoji="✨",
        category="style",
        result_key="style_findings",
        system_prompt=STYLE_PROMPT,
        taxonomy=STYLE_TAXONOMY,
        severities=STYLE_SEVERITIES,
        focus="Review the added lines for readability and maintainability problems that are objectively present.",
        default_severity="low",
    )