"""GitHub API client for fetching PRs and posting reviews.

Uses httpx for async HTTP requests to the GitHub REST API.
"""

import httpx
from typing import List, Dict, Optional

from reviewer.config import config


class GitHubClient:
    """Client for interacting with GitHub's REST API."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client.
        
        Args:
            token: GitHub personal access token. If None, uses config.github_token.
        """
        self.token = token or config.github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    
    async def get_pr(self, owner: str, repo: str, pr_number: int) -> Dict:
        """Fetch pull request metadata.
        
        Args:
            owner: Repository owner (username or org).
            repo: Repository name.
            pr_number: Pull request number.
            
        Returns:
            Dict with PR metadata (title, body, author, etc.).
            
        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch the list of files changed in a PR.
        
        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.
            
        Returns:
            List of dicts with file metadata (filename, additions, deletions, patch, etc.).
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    async def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch the unified diff for a PR.
        
        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.
            
        Returns:
            Unified diff as a string.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        # Request diff format using Accept header
        headers = {
            **self.headers,
            "Accept": "application/vnd.github.diff"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.text
    
    async def post_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
        comments: Optional[List[Dict]] = None
    ) -> Dict:
        """Post a review to a pull request.
        
        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.
            body: The review summary comment.
            event: Review event type: "COMMENT", "APPROVE", or "REQUEST_CHANGES".
            comments: Optional list of line comments with structure:
                [{"path": "file.py", "line": 10, "body": "comment text"}, ...]
                
        Returns:
            Dict with the created review metadata.
            
        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        payload = {
            "body": body,
            "event": event,
        }
        
        if comments:
            # Convert our simple format to GitHub's review comments format
            payload["comments"] = [
                {
                    "path": comment["path"],
                    "line": comment["line"],
                    "body": comment["body"]
                }
                for comment in comments
            ]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def post_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str
    ) -> Dict:
        """Post a simple comment to a pull request.
        
        This posts a general comment, not a review. Useful for dry-run mode.
        
        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.
            body: Comment text.
            
        Returns:
            Dict with the created comment metadata.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        payload = {"body": body}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
