"""Shared plumbing for the bug, security and style agents.

Each agent module only defines its prompt, issue taxonomy and severity levels.
Everything else (building the request, calling the LLM, parsing JSON, and
discarding findings that are not backed by the diff) lives here so the three
agents cannot drift apart.
"""

import json
import re
from typing import Dict, List, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from reviewer.llm import default_llm
from reviewer.state import ReviewState, ReviewFinding
from reviewer.utils import truncate_large_diff

MAX_DIFF_LINES = 1000
MIN_CONFIDENCE = 0.6   # findings below this are dropped
MAX_FINDINGS = 8       # hard cap per agent to limit noise


# --------------------------------------------------------------------------
# Request building
# --------------------------------------------------------------------------

def build_request(
    state: ReviewState,
    diff: str,
    category: str,
    taxonomy: Dict[str, str],
    severities: Tuple[str, ...],
    focus: str,
) -> str:
    """Build the user message sent to the LLM."""
    taxonomy_text = "\n".join(f"- {issue_id}: {desc}" for issue_id, desc in taxonomy.items())
    taxonomy_text += f"\n- other_{category}: a real issue that fits none of the ids above"

    schema = {
        "issue_id": "one id from the allowed list",
        "category": category,
        "severity": "|".join(severities),
        "confidence": 0.9,
        "file": "path/to/file",
        "line": 42,
        "title": "Brief issue description",
        "evidence": "exact added line(s) copied from the diff, without the leading +",
        "description": "What goes wrong, and for which input or situation",
        "suggestion": "How to fix it",
    }

    return f"""
# Pull Request Information
**Title:** {state.get('pr_title', 'N/A')}
**Author:** {state.get('pr_author', 'N/A')}
**Description:** {state.get('pr_body') or 'No description provided'}

# Files Changed
{len(state.get('files', []))} files changed

# Diff to Review
```diff
{diff}
```

# Allowed issue_id values
{taxonomy_text}

# Task
{focus}

Return ONLY a JSON array of objects with this structure (no prose, no markdown fences):
[
{json.dumps(schema, indent=2)}
]

If you find nothing that meets the criteria in your instructions, return an empty array: []
"""


# --------------------------------------------------------------------------
# Parsing and filtering
# --------------------------------------------------------------------------

def _collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def added_code(diff: str) -> str:
    """Return only the added lines of a diff, whitespace-collapsed."""
    lines = [
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    return _collapse_whitespace(" ".join(lines))


def _evidence_in_added_code(evidence: str, added: str) -> bool:
    """True if the quoted evidence really appears in the added lines."""
    cleaned = []
    for line in evidence.splitlines():
        line = line.strip()
        if line.startswith("+"):
            line = line[1:]
        cleaned.append(line)
    normalised = _collapse_whitespace(" ".join(cleaned))
    return bool(normalised) and normalised in added


def _load_json_items(response_text: str) -> list:
    """Extract a list of finding dicts from the raw LLM response."""
    text = response_text.strip()

    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("["), text.rfind("]")
        if start == -1 or end <= start:
            raise
        data = json.loads(text[start:end + 1])

    if isinstance(data, dict):
        if isinstance(data.get("findings"), list):
            return data["findings"]
        return [data] if "title" in data else []
    if isinstance(data, list):
        return data
    raise ValueError(f"Expected a JSON array, got {type(data).__name__}")


def _to_float(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalise_id(value) -> str:
    return re.sub(r"[\s\-]+", "_", str(value or "").strip().lower())


def parse_findings(
    response_text: str,
    *,
    category: str,
    taxonomy: Dict[str, str],
    severities: Tuple[str, ...],
    added: str,
    default_severity: str = "medium",
) -> Tuple[List[ReviewFinding], Dict[str, int]]:
    """Parse the LLM response into validated findings.

    Drops findings that are malformed, below MIN_CONFIDENCE, duplicated, or whose
    `evidence` does not appear in the added lines of the diff.

    Returns:
        (findings, dropped) where dropped counts discarded items by reason.
    """
    items = _load_json_items(response_text)
    allowed_ids = set(taxonomy) | {f"other_{category}"}
    dropped = {"malformed": 0, "low_confidence": 0, "unsupported_evidence": 0, "duplicate": 0}

    findings: List[ReviewFinding] = []
    seen = set()

    for item in items:
        if not isinstance(item, dict) or not item.get("title"):
            dropped["malformed"] += 1
            continue

        confidence = _to_float(item.get("confidence"), MIN_CONFIDENCE)
        if confidence < MIN_CONFIDENCE:
            dropped["low_confidence"] += 1
            continue

        evidence = str(item.get("evidence") or "")
        if not _evidence_in_added_code(evidence, added):
            dropped["unsupported_evidence"] += 1
            continue

        issue_id = _normalise_id(item.get("issue_id"))
        if issue_id not in allowed_ids:
            issue_id = f"other_{category}"

        severity = str(item.get("severity") or "").strip().lower()
        if severity not in severities:
            severity = default_severity

        file = str(item.get("file") or "unknown")
        line = _to_int(item.get("line"))

        key = (issue_id, file, line)
        if key in seen:
            dropped["duplicate"] += 1
            continue
        seen.add(key)

        findings.append(ReviewFinding(
            issue_id=issue_id,
            category=category,
            severity=severity,
            file=file,
            line=line,
            title=str(item["title"]).strip(),
            description=str(item.get("description") or "").strip(),
            suggestion=str(item.get("suggestion") or "").strip(),
            evidence=evidence.strip(),
            confidence=confidence,
        ))

    findings.sort(key=lambda f: f["confidence"], reverse=True)
    return findings[:MAX_FINDINGS], dropped


# --------------------------------------------------------------------------
# Agent runner
# --------------------------------------------------------------------------

async def run_agent(
    *,
    state: ReviewState,
    label: str,
    emoji: str,
    category: str,
    result_key: str,
    system_prompt: str,
    taxonomy: Dict[str, str],
    severities: Tuple[str, ...],
    focus: str,
    default_severity: str = "medium",
) -> dict:
    """Run one review agent end to end and return {result_key: findings}."""
    print(f"{emoji} {label}: Analyzing...")

    full_diff = state.get("full_diff", "")
    if not full_diff:
        print("   No diff to analyze")
        return {result_key: []}

    diff_to_analyze = truncate_large_diff(full_diff, max_lines=MAX_DIFF_LINES)
    request = build_request(state, diff_to_analyze, category, taxonomy, severities, focus)

    try:
        response = await default_llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=request),
        ])
        findings, dropped = parse_findings(
            response.content,
            category=category,
            taxonomy=taxonomy,
            severities=severities,
            added=added_code(full_diff),
            default_severity=default_severity,
        )
    except json.JSONDecodeError as e:
        print(f"   ⚠️  Failed to parse JSON response: {e}")
        return {result_key: []}
    except Exception as e:
        print(f"   ⚠️  Error in {label}: {e}")
        return {result_key: []}

    discarded = sum(dropped.values())
    suffix = f" ({discarded} discarded: {dropped})" if discarded else ""
    print(f"   Found {len(findings)} {category} issue(s){suffix}")
    return {result_key: findings}