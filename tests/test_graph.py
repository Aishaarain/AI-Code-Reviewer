"""Tests for the LangGraph workflow."""

import pytest

from reviewer.graph import create_review_graph
from reviewer.state import create_initial_state


def test_create_review_graph():
    """Test that the review graph can be created."""
    graph = create_review_graph()
    assert graph is not None


def test_initial_state_creation():
    """Test creating initial state."""
    state = create_initial_state("owner", "repo", 123, "https://github.com/owner/repo/pull/123")
    
    assert state["owner"] == "owner"
    assert state["repo"] == "repo"
    assert state["pr_number"] == 123
    assert state["pr_url"] == "https://github.com/owner/repo/pull/123"
    assert state["bug_findings"] == []
    assert state["security_findings"] == []
    assert state["style_findings"] == []
    assert state["should_post"] is False


@pytest.mark.asyncio
async def test_graph_structure():
    """Test that the graph has the expected structure."""
    graph = create_review_graph()
    
    # The graph should be compiled and ready
    assert graph is not None
    
    # Test would require mocking GitHub API calls for full execution
    # For now, just verify it can be created
