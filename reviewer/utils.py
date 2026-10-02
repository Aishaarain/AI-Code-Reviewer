"""Utility functions for the code reviewer.

Includes PR URL parsing, diff filtering, and text processing.
"""

import re
from typing import Optional, Tuple, List


def parse_pr_url(url: str) -> Tuple[str, str, int]:
    """Parse a GitHub PR URL into owner, repo, and PR number.
    
    Args:
        url: GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)
        
    Returns:
        Tuple of (owner, repo, pr_number)
        
    Raises:
        ValueError: If URL is not a valid GitHub PR URL.
        
    Examples:
        >>> parse_pr_url("https://github.com/torvalds/linux/pull/42")
        ('torvalds', 'linux', 42)
    """
    # Pattern matches:
    # https://github.com/owner/repo/pull/123
    # http://github.com/owner/repo/pull/123
    # github.com/owner/repo/pull/123
    pattern = r"(?:https?://)?github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.match(pattern, url.strip())
    
    if not match:
        raise ValueError(
            f"Invalid GitHub PR URL: {url}\n"
            "Expected format: https://github.com/owner/repo/pull/123"
        )
    
    owner, repo, pr_num = match.groups()
    return owner, repo, int(pr_num)


def should_skip_file(filename: str) -> bool:
    """Determine if a file should be skipped during review.
    
    Skips lockfiles, generated files, binaries, and large data files.
    
    Args:
        filename: The file path to check.
        
    Returns:
        True if the file should be skipped, False otherwise.
        
    Examples:
        >>> should_skip_file("package-lock.json")
        True
        >>> should_skip_file("src/main.py")
        False
    """
    skip_patterns = [
        # Lockfiles
        r"package-lock\.json$",
        r"yarn\.lock$",
        r"pnpm-lock\.yaml$",
        r"Gemfile\.lock$",
        r"poetry\.lock$",
        r"Pipfile\.lock$",
        
        # Generated/minified code
        r"\.min\.(js|css)$",
        r"\.bundle\.(js|css)$",
        r"bundle\.js$",
        r"bundle\.css$",
        r"-dist\.",
        r"(^|/)dist/",
        r"(^|/)build/",
        r"(^|/)__pycache__/",
        
        # Binary/data files
        r"\.(png|jpg|jpeg|gif|ico|svg|pdf|zip|tar|gz)$",
        r"\.(woff|woff2|ttf|eot)$",
        r"\.(exe|dll|so|dylib)$",
    ]
    
    for pattern in skip_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    
    return False


def filter_files(files: List[dict]) -> List[dict]:
    """Filter out files that should be skipped from review.
    
    Args:
        files: List of file dicts from GitHub API with 'filename' key.
        
    Returns:
        Filtered list of files that should be reviewed.
    """
    return [f for f in files if not should_skip_file(f.get("filename", ""))]


def truncate_large_diff(diff: str, max_lines: int = 500) -> str:
    """Truncate large diffs to prevent token overflow.
    
    Args:
        diff: The diff text to truncate.
        max_lines: Maximum number of lines to keep.
        
    Returns:
        Truncated diff with a notice if truncation occurred.
    """
    lines = diff.split("\n")
    
    if len(lines) <= max_lines:
        return diff
    
    truncated = "\n".join(lines[:max_lines])
    notice = (
        f"\n\n... [TRUNCATED: {len(lines) - max_lines} lines omitted] ...\n"
        f"(File is too large for full review. Showing first {max_lines} lines.)"
    )
    
    return truncated + notice


def split_diff_by_file(full_diff: str) -> dict[str, str]:
    """Split a unified diff into per-file diffs.
    
    Args:
        full_diff: Complete diff text from GitHub.
        
    Returns:
        Dict mapping filename to its diff content.
        
    Example:
        Input: "diff --git a/file1.py ... diff --git a/file2.py ..."
        Output: {"file1.py": "diff --git a/file1.py ...", "file2.py": "..."}
    """
    file_diffs = {}
    current_file = None
    current_diff_lines = []
    
    for line in full_diff.split("\n"):
        # New file starts with "diff --git"
        if line.startswith("diff --git"):
            # Save previous file
            if current_file:
                file_diffs[current_file] = "\n".join(current_diff_lines)
            
            # Extract filename from: "diff --git a/path/file.py b/path/file.py"
            match = re.search(r"b/(.+)$", line)
            if match:
                current_file = match.group(1)
                current_diff_lines = [line]
            else:
                current_file = None
                current_diff_lines = []
        elif current_file:
            current_diff_lines.append(line)
    
    # Save last file
    if current_file:
        file_diffs[current_file] = "\n".join(current_diff_lines)
    
    return file_diffs


def format_file_summary(files: List[dict]) -> str:
    """Format a list of changed files into a readable summary.
    
    Args:
        files: List of file dicts from GitHub API.
        
    Returns:
        Formatted string listing files with their change stats.
        
    Example:
        "3 files changed:\n  src/main.py (+15, -3)\n  ..."
    """
    if not files:
        return "No files changed."
    
    summary_lines = [f"{len(files)} file(s) changed:"]
    
    for file in files:
        filename = file.get("filename", "unknown")
        additions = file.get("additions", 0)
        deletions = file.get("deletions", 0)
        status = file.get("status", "modified")
        
        summary_lines.append(f"  [{status}] {filename} (+{additions}, -{deletions})")
    
    return "\n".join(summary_lines)
