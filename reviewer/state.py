# """State definition for the LangGraph workflow.

# The state is shared across all nodes in the graph and accumulates
# information as the workflow progresses.
# """

# from typing import List, Dict, Optional, TypedDict, Annotated
# from operator import add


# class ReviewFinding(TypedDict, total=False):
#     """A single review finding from an agent.
    
#     Attributes:
#         category: The finding category (bug, security, style, etc.).
#         severity: Severity level (critical, high, medium, low, info).
#         file: The file where the issue was found.
#         line: Line number (if applicable).
#         title: Short title of the finding.
#         description: Detailed description of the issue.
#         suggestion: Suggested fix or improvement.
#     """
#     category: str
#     severity: str
#     file: str
#     line: Optional[int]
#     title: str
#     description: str
#     suggestion: Optional[str]


# class ReviewState(TypedDict, total=False):
#     """State that flows through the review workflow.
    
#     This state is updated by each node in the LangGraph workflow.
#     Fields that can be updated by multiple parallel nodes use Annotated with 'add' reducer.
#     """
#     # Input data (only set once at start)
#     owner: str
#     repo: str
#     pr_number: int
#     pr_url: str
    
#     # PR metadata (set by fetch_pr node)
#     pr_title: str
#     pr_body: str
#     pr_author: str
    
#     # PR changes (set by fetch_pr node)
#     files: List[Dict]  # List of file metadata from GitHub
#     full_diff: str
#     file_diffs: Dict[str, str]  # Maps filename to its diff
    
#     # Review findings from each agent (use Annotated to handle parallel updates)
#     bug_findings: Annotated[List[ReviewFinding], add]
#     security_findings: Annotated[List[ReviewFinding], add]
#     style_findings: Annotated[List[ReviewFinding], add]
    
#     # Final synthesized review (set by synthesizer)
#     final_review: str
#     summary: str
    
#     # Metadata
#     should_post: bool
#     error: Optional[str]


# def create_initial_state(owner: str, repo: str, pr_number: int, pr_url: str) -> ReviewState:
#     """Create an initial state for the review workflow.
    
#     Args:
#         owner: Repository owner.
#         repo: Repository name.
#         pr_number: Pull request number.
#         pr_url: Full PR URL.
        
#     Returns:
#         Initial ReviewState with empty findings lists.
#     """
#     return ReviewState(
#         owner=owner,
#         repo=repo,
#         pr_number=pr_number,
#         pr_url=pr_url,
#         pr_title="",
#         pr_body="",
#         pr_author="",
#         files=[],
#         full_diff="",
#         file_diffs={},
#         bug_findings=[],
#         security_findings=[],
#         style_findings=[],
#         final_review="",
#         summary="",
#         should_post=False,
#         error=None,
#     )



"""State definition for the LangGraph workflow.

The state is shared across all nodes in the graph and accumulates
information as the workflow progresses.
"""

from typing import List, Dict, Optional, TypedDict, Annotated
from operator import add


class ReviewFinding(TypedDict, total=False):
    """A single review finding from an agent.

    Attributes:
        issue_id: Stable machine-readable id from the agent's taxonomy
            (e.g. "sql_injection"). Used for evaluation instead of free-text titles.
        category: The finding category (bug, security, style).
        severity: Severity level (critical, high, medium, low, info).
        file: The file where the issue was found.
        line: Line number (if applicable).
        title: Short title of the finding.
        description: Detailed description of the issue.
        suggestion: Suggested fix or improvement.
        evidence: Exact added line(s) from the diff that show the problem.
            Findings whose evidence is not in the diff are discarded.
        confidence: Agent's confidence between 0 and 1.
    """
    issue_id: str
    category: str
    severity: str
    file: str
    line: Optional[int]
    title: str
    description: str
    suggestion: Optional[str]
    evidence: str
    confidence: float


class ReviewState(TypedDict, total=False):
    """State that flows through the review workflow.

    This state is updated by each node in the LangGraph workflow.
    Fields that can be updated by multiple parallel nodes use Annotated with 'add' reducer.
    """
    # Input data (only set once at start)
    owner: str
    repo: str
    pr_number: int
    pr_url: str

    # PR metadata (set by fetch_pr node)
    pr_title: str
    pr_body: str
    pr_author: str

    # PR changes (set by fetch_pr node)
    files: List[Dict]  # List of file metadata from GitHub
    full_diff: str
    file_diffs: Dict[str, str]  # Maps filename to its diff

    # Review findings from each agent (use Annotated to handle parallel updates)
    bug_findings: Annotated[List[ReviewFinding], add]
    security_findings: Annotated[List[ReviewFinding], add]
    style_findings: Annotated[List[ReviewFinding], add]

    # Final synthesized review (set by synthesizer)
    final_review: str
    summary: str

    # Metadata
    should_post: bool
    error: Optional[str]


def create_initial_state(owner: str, repo: str, pr_number: int, pr_url: str) -> ReviewState:
    """Create an initial state for the review workflow.

    Args:
        owner: Repository owner.
        repo: Repository name.
        pr_number: Pull request number.
        pr_url: Full PR URL.

    Returns:
        Initial ReviewState with empty findings lists.
    """
    return ReviewState(
        owner=owner,
        repo=repo,
        pr_number=pr_number,
        pr_url=pr_url,
        pr_title="",
        pr_body="",
        pr_author="",
        files=[],
        full_diff="",
        file_diffs={},
        bug_findings=[],
        security_findings=[],
        style_findings=[],
        final_review="",
        summary="",
        should_post=False,
        error=None,
    )