# """Security review agent for code reviews.

# Identifies security vulnerabilities and risks in code changes.
# """

# import json
# from pathlib import Path
# from typing import List

# from langchain_core.messages import HumanMessage, SystemMessage

# from reviewer.llm import default_llm
# from reviewer.state import ReviewState, ReviewFinding
# from reviewer.utils import truncate_large_diff


# # Load the security review prompt
# PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "security.md"
# SECURITY_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")


# async def security_agent(state: ReviewState) -> dict:
#     """Analyze code changes for security vulnerabilities.
    
#     Args:
#         state: Current review state with PR data and diffs.
        
#     Returns:
#         Dict with security_findings key.
#     """
#     print("🔒 Security Agent: Analyzing for vulnerabilities...")
    
#     # Get the diff to analyze
#     full_diff = state.get("full_diff", "")
#     if not full_diff:
#         print("   No diff to analyze")
#         return {"security_findings": []}
    
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

# Please analyze the above changes for security vulnerabilities and risks.
# Return your findings as a JSON array of objects with this structure:
# [
#   {{
#     "category": "security",
#     "severity": "critical|high|medium|low",
#     "file": "path/to/file",
#     "line": 42,
#     "title": "Brief security issue description",
#     "description": "Detailed explanation of the vulnerability",
#     "suggestion": "How to mitigate"
#   }}
# ]

# If no security issues found, return an empty array: []
# """
    
#     try:
#         # Call the LLM
#         messages = [
#             SystemMessage(content=SECURITY_PROMPT),
#             HumanMessage(content=pr_context)
#         ]
        
#         response = await default_llm.ainvoke(messages)
        
#         # Parse the response
#         findings = parse_findings(response.content)
        
#         print(f"   Found {len(findings)} security issue(s)")
#         return {"security_findings": findings}
        
#     except Exception as e:
#         print(f"   ⚠️  Error in security agent: {e}")
#         return {"security_findings": []}


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


"""Security review agent for code reviews.

Identifies security vulnerabilities and risks in code changes.
"""

from pathlib import Path

from reviewer.agents.base import run_agent
from reviewer.state import ReviewState

# Load the security review prompt
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "security.md"
SECURITY_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")

SECURITY_TAXONOMY = {
    "sql_injection": "SQL built from untrusted input by string formatting/concatenation",
    "command_injection": "Shell command built from untrusted input (os.system, shell=True, ...)",
    "code_injection": "eval/exec/dynamic code execution on untrusted data",
    "path_traversal": "File path built from untrusted input without confinement",
    "xss": "Untrusted input rendered into HTML/JS without escaping",
    "insecure_deserialization": "pickle/yaml.load/etc. on untrusted data",
    "ssrf": "Server-side request made to a URL controlled by the user",
    "hardcoded_secret": "Password, API key, token or private key committed in source",
    "weak_crypto": "Broken or unsuitable crypto (MD5/SHA1 for passwords, ECB, insecure random for secrets)",
    "weak_authentication": "Authentication logic that can be bypassed or is trivially weak",
    "missing_access_control": "Sensitive operation exposed with no authorization check visible in the diff",
    "sensitive_data_exposure": "Secrets or personal data written to logs, responses or error messages",
}

SECURITY_SEVERITIES = ("critical", "high", "medium", "low")


async def security_agent(state: ReviewState) -> dict:
    """Analyze code changes for security vulnerabilities.

    Args:
        state: Current review state with PR data and diffs.

    Returns:
        Dict with security_findings key.
    """
    return await run_agent(
        state=state,
        label="Security Agent",
        emoji="🔒",
        category="security",
        result_key="security_findings",
        system_prompt=SECURITY_PROMPT,
        taxonomy=SECURITY_TAXONOMY,
        severities=SECURITY_SEVERITIES,
        focus="Review the added lines for exploitable security vulnerabilities.",
        default_severity="medium",
    )