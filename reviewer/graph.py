"""LangGraph workflow for the code review process.

Defines the graph structure: fetch PR → parallel agents → synthesizer → post review.
"""

from langgraph.graph import StateGraph, END

from reviewer.state import ReviewState, create_initial_state
from reviewer.github_client import GitHubClient
from reviewer.agents.bug_agent import bug_agent
from reviewer.agents.security_agent import security_agent
from reviewer.agents.style_agent import style_agent
from reviewer.agents.synthesizer import synthesizer_agent
from reviewer.utils import filter_files, split_diff_by_file, format_file_summary


async def fetch_pr_node(state: ReviewState) -> ReviewState:
    """Fetch PR metadata and changes from GitHub.
    
    Args:
        state: Initial state with owner, repo, pr_number.
        
    Returns:
        Updated state with PR data and diff.
    """
    print(f"📥 Fetching PR #{state['pr_number']} from {state['owner']}/{state['repo']}...")
    
    client = GitHubClient()
    owner = state["owner"]
    repo = state["repo"]
    pr_number = state["pr_number"]
    
    try:
        # Fetch PR metadata
        pr_data = await client.get_pr(owner, repo, pr_number)
        state["pr_title"] = pr_data.get("title", "")
        state["pr_body"] = pr_data.get("body", "")
        state["pr_author"] = pr_data.get("user", {}).get("login", "unknown")
        
        print(f"   Title: {state['pr_title']}")
        print(f"   Author: @{state['pr_author']}")
        
        # Fetch changed files
        files = await client.get_pr_files(owner, repo, pr_number)
        print(f"\n   {format_file_summary(files)}")
        
        # Filter out files we should skip
        filtered_files = filter_files(files)
        if len(filtered_files) < len(files):
            print(f"   Filtered to {len(filtered_files)} reviewable files (skipped binaries, lockfiles, etc.)")
        
        state["files"] = filtered_files
        
        # Fetch the full diff
        full_diff = await client.get_pr_diff(owner, repo, pr_number)
        state["full_diff"] = full_diff
        
        # Split diff by file for easier analysis
        file_diffs = split_diff_by_file(full_diff)
        state["file_diffs"] = file_diffs
        
        print(f"   ✅ Fetched diff ({len(full_diff)} characters)\n")
        
    except Exception as e:
        print(f"   ❌ Error fetching PR: {e}")
        state["error"] = str(e)
    
    return state


async def post_review_node(state: ReviewState) -> ReviewState:
    """Post the review back to GitHub.
    
    Args:
        state: State with final_review populated.
        
    Returns:
        Updated state.
    """
    should_post = state.get("should_post", False)
    
    if not should_post:
        print("\n📝 Dry-run mode: Review not posted to GitHub")
        print("\n" + "="*80)
        print(state.get("final_review", "No review generated"))
        print("="*80 + "\n")
        return state
    
    print("\n📤 Posting review to GitHub...")
    
    client = GitHubClient()
    owner = state["owner"]
    repo = state["repo"]
    pr_number = state["pr_number"]
    review_body = state.get("final_review", "Automated review completed.")
    
    try:
        result = await client.post_review(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            body=review_body,
            event="COMMENT"
        )
        
        print(f"   ✅ Review posted successfully!")
        print(f"   View at: {state['pr_url']}")
        
    except Exception as e:
        print(f"   ❌ Error posting review: {e}")
        state["error"] = str(e)
    
    return state


def create_review_graph() -> StateGraph:
    """Create the LangGraph workflow for code review.
    
    Returns:
        Compiled StateGraph ready to execute.
    """
    # Create the graph
    workflow = StateGraph(ReviewState)
    
    # Add nodes
    workflow.add_node("fetch_pr", fetch_pr_node)
    workflow.add_node("bug_agent", bug_agent)
    workflow.add_node("security_agent", security_agent)
    workflow.add_node("style_agent", style_agent)
    workflow.add_node("synthesizer", synthesizer_agent)
    workflow.add_node("post_review", post_review_node)
    
    # Define the flow
    workflow.set_entry_point("fetch_pr")
    
    # After fetching PR, run all three agents in parallel
    workflow.add_edge("fetch_pr", "bug_agent")
    workflow.add_edge("fetch_pr", "security_agent")
    workflow.add_edge("fetch_pr", "style_agent")
    
    # After all agents complete, run synthesizer
    workflow.add_edge("bug_agent", "synthesizer")
    workflow.add_edge("security_agent", "synthesizer")
    workflow.add_edge("style_agent", "synthesizer")
    
    # After synthesis, post the review
    workflow.add_edge("synthesizer", "post_review")
    
    # End after posting
    workflow.add_edge("post_review", END)
    
    return workflow.compile()


async def run_review(owner: str, repo: str, pr_number: int, pr_url: str, should_post: bool = False):
    """Run the complete code review workflow.
    
    Args:
        owner: Repository owner.
        repo: Repository name.
        pr_number: Pull request number.
        pr_url: Full PR URL.
        should_post: If True, post review to GitHub. If False, print to console.
        
    Returns:
        Final review state.
    """
    print("\n🚀 Starting Agentic Code Review\n")
    
    # Create initial state
    initial_state = create_initial_state(owner, repo, pr_number, pr_url)
    initial_state["should_post"] = should_post
    
    # Create and run the graph
    graph = create_review_graph()
    
    # Execute the workflow
    final_state = await graph.ainvoke(initial_state)
    
    print("\n✅ Review complete!\n")
    
    return final_state
