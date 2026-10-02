"""Synthesizer agent that combines findings from all review agents.

Takes bug, security, and style findings and produces a unified, prioritized review.
"""

import json
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from reviewer.llm import create_llm
from reviewer.state import ReviewState, ReviewFinding


# Load the synthesizer prompt
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "synthesizer.md"
SYNTHESIZER_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")


async def synthesizer_agent(state: ReviewState) -> dict:
    """Synthesize findings from all agents into a final review.
    
    Args:
        state: Review state with bug_findings, security_findings, style_findings.
        
    Returns:
        Dict with final_review and summary keys.
    """
    print("🔄 Synthesizer: Combining and prioritizing findings...")
    
    # Collect all findings
    bug_findings = state.get("bug_findings", [])
    security_findings = state.get("security_findings", [])
    style_findings = state.get("style_findings", [])
    
    total_findings = len(bug_findings) + len(security_findings) + len(style_findings)
    
    if total_findings == 0:
        print("   No findings to synthesize - generating positive review")
        final_review = generate_clean_review(state)
        return {
            "final_review": final_review,
            "summary": "No significant issues found. Code looks good! ✅"
        }
    
    print(f"   Synthesizing {total_findings} findings ({len(bug_findings)} bugs, "
          f"{len(security_findings)} security, {len(style_findings)} style)")
    
    # Format findings for the LLM
    findings_text = format_findings_for_synthesis(bug_findings, security_findings, style_findings)
    
    # Prepare the synthesis prompt
    pr_info = f"""
# Pull Request Context
**Title:** {state.get('pr_title', 'N/A')}
**Author:** {state.get('pr_author', 'N/A')}
**Files Changed:** {len(state.get('files', []))}

# Findings from Review Agents

{findings_text}

Please synthesize these findings into a cohesive, well-structured code review.
Follow the format specified in your instructions.
"""
    
    try:
        # Use a higher temperature for more natural synthesis
        llm = create_llm(temperature=0.3, max_tokens=8192)
        
        messages = [
            SystemMessage(content=SYNTHESIZER_PROMPT),
            HumanMessage(content=pr_info)
        ]
        
        response = await llm.ainvoke(messages)
        final_review = response.content.strip()
        
        # Extract a brief summary (first paragraph or first 200 chars)
        summary = extract_summary(final_review)
        
        print(f"   ✅ Synthesis complete")
        return {
            "final_review": final_review,
            "summary": summary
        }
        
    except Exception as e:
        print(f"   ⚠️  Error in synthesizer: {e}")
        # Fallback: create a simple formatted review
        fallback_review = create_fallback_review(bug_findings, security_findings, style_findings)
        return {
            "final_review": fallback_review,
            "summary": f"Found {total_findings} issues across bug, security, and style categories."
        }


def format_findings_for_synthesis(
    bug_findings: list,
    security_findings: list,
    style_findings: list
) -> str:
    """Format findings into a readable text for the synthesizer.
    
    Args:
        bug_findings: List of bug findings.
        security_findings: List of security findings.
        style_findings: List of style findings.
        
    Returns:
        Formatted string with all findings.
    """
    sections = []
    
    if bug_findings:
        sections.append("## Bug Findings\n")
        for i, finding in enumerate(bug_findings, 1):
            sections.append(format_single_finding(i, finding))
    
    if security_findings:
        sections.append("\n## Security Findings\n")
        for i, finding in enumerate(security_findings, 1):
            sections.append(format_single_finding(i, finding))
    
    if style_findings:
        sections.append("\n## Style Findings\n")
        for i, finding in enumerate(style_findings, 1):
            sections.append(format_single_finding(i, finding))
    
    return "\n".join(sections)


def format_single_finding(index: int, finding: ReviewFinding) -> str:
    """Format a single finding for display.
    
    Args:
        index: Finding number.
        finding: ReviewFinding dict.
        
    Returns:
        Formatted string.
    """
    file_info = finding.get("file", "unknown")
    line = finding.get("line")
    if line:
        file_info += f":{line}"
    
    return f"""
### {index}. {finding.get('title', 'Issue')}
- **File:** `{file_info}`
- **Severity:** {finding.get('severity', 'unknown')}
- **Description:** {finding.get('description', 'No description')}
- **Suggestion:** {finding.get('suggestion', 'No suggestion provided')}
"""


def extract_summary(review_text: str) -> str:
    """Extract a brief summary from the full review.
    
    Args:
        review_text: Full review markdown text.
        
    Returns:
        Brief summary string.
    """
    lines = review_text.split("\n")
    
    # Try to find the overview section
    for i, line in enumerate(lines):
        if "## Overview" in line and i + 1 < len(lines):
            # Return the next non-empty line
            for j in range(i + 1, min(i + 5, len(lines))):
                if lines[j].strip():
                    return lines[j].strip()
    
    # Fallback: return first 200 characters
    clean_text = review_text.replace("#", "").strip()
    return clean_text[:200] + ("..." if len(clean_text) > 200 else "")


def generate_clean_review(state: ReviewState) -> str:
    """Generate a positive review when no issues are found.
    
    Args:
        state: Review state.
        
    Returns:
        Positive review text.
    """
    return f"""# Code Review Summary

## Overview
Reviewed **{len(state.get('files', []))}** file(s) in this pull request. No significant issues were identified by the automated review agents.

## Analysis Results ✅

- **Bug Detection:** No logic errors or edge cases identified
- **Security Review:** No vulnerabilities detected
- **Code Quality:** No maintainability concerns raised

## Recommendation

The code appears to be well-written and ready for merge. Consider having a human reviewer give it a final look to ensure alignment with team standards and business requirements.

---

*This is an automated review. Always use human judgment for final approval decisions.*
"""


def create_fallback_review(
    bug_findings: list,
    security_findings: list,
    style_findings: list
) -> str:
    """Create a simple fallback review if synthesis fails.
    
    Args:
        bug_findings: List of bug findings.
        security_findings: List of security findings.
        style_findings: List of style findings.
        
    Returns:
        Basic formatted review.
    """
    sections = ["# Code Review\n\n## Findings\n"]
    
    all_findings = [
        ("Bug", bug_findings),
        ("Security", security_findings),
        ("Style", style_findings)
    ]
    
    for category, findings in all_findings:
        if findings:
            sections.append(f"\n### {category} Issues ({len(findings)})\n")
            for finding in findings:
                sections.append(f"- **{finding.get('title')}** in `{finding.get('file')}`: "
                              f"{finding.get('description')}\n")
    
    sections.append("\n---\n*Automated review - synthesis error occurred*")
    
    return "".join(sections)
