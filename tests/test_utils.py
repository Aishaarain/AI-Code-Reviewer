"""Tests for utility functions."""

import pytest

from reviewer.utils import (
    parse_pr_url,
    should_skip_file,
    filter_files,
    truncate_large_diff,
    split_diff_by_file,
    format_file_summary,
)


class TestParsePrUrl:
    """Tests for parse_pr_url function."""
    
    def test_https_url(self):
        """Test parsing HTTPS GitHub PR URL."""
        owner, repo, pr_num = parse_pr_url("https://github.com/torvalds/linux/pull/42")
        assert owner == "torvalds"
        assert repo == "linux"
        assert pr_num == 42
    
    def test_http_url(self):
        """Test parsing HTTP GitHub PR URL."""
        owner, repo, pr_num = parse_pr_url("http://github.com/python/cpython/pull/123")
        assert owner == "python"
        assert repo == "cpython"
        assert pr_num == 123
    
    def test_url_without_protocol(self):
        """Test parsing URL without protocol."""
        owner, repo, pr_num = parse_pr_url("github.com/facebook/react/pull/999")
        assert owner == "facebook"
        assert repo == "react"
        assert pr_num == 999
    
    def test_url_with_whitespace(self):
        """Test parsing URL with leading/trailing whitespace."""
        owner, repo, pr_num = parse_pr_url("  https://github.com/rust-lang/rust/pull/1  ")
        assert owner == "rust-lang"
        assert repo == "rust"
        assert pr_num == 1
    
    def test_invalid_url_no_pull(self):
        """Test that non-PR URLs raise ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
            parse_pr_url("https://github.com/owner/repo/issues/123")
    
    def test_invalid_url_wrong_domain(self):
        """Test that non-GitHub URLs raise ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
            parse_pr_url("https://gitlab.com/owner/repo/pull/123")
    
    def test_invalid_url_malformed(self):
        """Test that malformed URLs raise ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
            parse_pr_url("not a url")


class TestShouldSkipFile:
    """Tests for should_skip_file function."""
    
    def test_lockfiles_are_skipped(self):
        """Test that various lockfiles are skipped."""
        assert should_skip_file("package-lock.json") is True
        assert should_skip_file("yarn.lock") is True
        assert should_skip_file("pnpm-lock.yaml") is True
        assert should_skip_file("Gemfile.lock") is True
        assert should_skip_file("poetry.lock") is True
        assert should_skip_file("Pipfile.lock") is True
    
    def test_minified_files_are_skipped(self):
        """Test that minified/bundled files are skipped."""
        assert should_skip_file("app.min.js") is True
        assert should_skip_file("style.min.css") is True
        assert should_skip_file("bundle.js") is True
        assert should_skip_file("main.bundle.css") is True
    
    def test_generated_directories_are_skipped(self):
        """Test that files in generated directories are skipped."""
        assert should_skip_file("dist/main.js") is True
        assert should_skip_file("build/index.html") is True
        assert should_skip_file("src/__pycache__/module.pyc") is True
    
    def test_binary_files_are_skipped(self):
        """Test that binary files are skipped."""
        assert should_skip_file("logo.png") is True
        assert should_skip_file("photo.jpg") is True
        assert should_skip_file("document.pdf") is True
        assert should_skip_file("archive.zip") is True
        assert should_skip_file("font.woff2") is True
        assert should_skip_file("app.exe") is True
    
    def test_source_files_are_not_skipped(self):
        """Test that normal source files are not skipped."""
        assert should_skip_file("src/main.py") is False
        assert should_skip_file("index.html") is False
        assert should_skip_file("styles.css") is False
        assert should_skip_file("app.js") is False
        assert should_skip_file("README.md") is False
        assert should_skip_file("config.json") is False


class TestFilterFiles:
    """Tests for filter_files function."""
    
    def test_filters_out_skipped_files(self):
        """Test that filter_files removes files that should be skipped."""
        files = [
            {"filename": "src/main.py"},
            {"filename": "package-lock.json"},
            {"filename": "README.md"},
            {"filename": "logo.png"},
            {"filename": "config.yaml"},
        ]
        filtered = filter_files(files)
        
        assert len(filtered) == 3
        filenames = [f["filename"] for f in filtered]
        assert "src/main.py" in filenames
        assert "README.md" in filenames
        assert "config.yaml" in filenames
        assert "package-lock.json" not in filenames
        assert "logo.png" not in filenames
    
    def test_empty_list(self):
        """Test filtering empty list."""
        assert filter_files([]) == []
    
    def test_all_files_skipped(self):
        """Test when all files should be skipped."""
        files = [
            {"filename": "package-lock.json"},
            {"filename": "yarn.lock"},
        ]
        assert filter_files(files) == []


class TestTruncateLargeDiff:
    """Tests for truncate_large_diff function."""
    
    def test_small_diff_not_truncated(self):
        """Test that small diffs are not truncated."""
        diff = "line 1\nline 2\nline 3"
        result = truncate_large_diff(diff, max_lines=100)
        assert result == diff
        assert "TRUNCATED" not in result
    
    def test_large_diff_is_truncated(self):
        """Test that large diffs are truncated."""
        lines = [f"line {i}" for i in range(600)]
        diff = "\n".join(lines)
        
        result = truncate_large_diff(diff, max_lines=500)
        
        assert "line 0" in result
        assert "line 499" in result
        assert "line 500" not in result
        assert "TRUNCATED" in result
        assert "100 lines omitted" in result
    
    def test_custom_max_lines(self):
        """Test truncation with custom max_lines."""
        lines = [f"line {i}" for i in range(20)]
        diff = "\n".join(lines)
        
        result = truncate_large_diff(diff, max_lines=10)
        
        assert "line 0" in result
        assert "line 9" in result
        assert "line 10" not in result
        assert "10 lines omitted" in result


class TestSplitDiffByFile:
    """Tests for split_diff_by_file function."""
    
    def test_single_file_diff(self):
        """Test splitting diff with a single file."""
        diff = """diff --git a/file1.py b/file1.py
index abc123..def456 100644
--- a/file1.py
+++ b/file1.py
@@ -1,3 +1,3 @@
-old line
+new line
"""
        result = split_diff_by_file(diff)
        
        assert len(result) == 1
        assert "file1.py" in result
        assert "diff --git" in result["file1.py"]
        assert "new line" in result["file1.py"]
    
    def test_multiple_files_diff(self):
        """Test splitting diff with multiple files."""
        diff = """diff --git a/file1.py b/file1.py
index abc123..def456 100644
--- a/file1.py
+++ b/file1.py
@@ -1 +1 @@
-old
+new
diff --git a/file2.js b/file2.js
index 111222..333444 100644
--- a/file2.js
+++ b/file2.js
@@ -1 +1 @@
-old js
+new js
"""
        result = split_diff_by_file(diff)
        
        assert len(result) == 2
        assert "file1.py" in result
        assert "file2.js" in result
        assert "new" in result["file1.py"]
        assert "new js" in result["file2.js"]
    
    def test_empty_diff(self):
        """Test splitting empty diff."""
        result = split_diff_by_file("")
        assert result == {}
    
    def test_files_with_paths(self):
        """Test files with directory paths."""
        diff = """diff --git a/src/utils/helper.py b/src/utils/helper.py
index abc..def 100644
--- a/src/utils/helper.py
+++ b/src/utils/helper.py
@@ -1 +1 @@
-old
+new
"""
        result = split_diff_by_file(diff)
        
        assert len(result) == 1
        assert "src/utils/helper.py" in result


class TestFormatFileSummary:
    """Tests for format_file_summary function."""
    
    def test_empty_files_list(self):
        """Test formatting empty files list."""
        result = format_file_summary([])
        assert result == "No files changed."
    
    def test_single_file(self):
        """Test formatting single file."""
        files = [
            {
                "filename": "src/main.py",
                "additions": 10,
                "deletions": 5,
                "status": "modified"
            }
        ]
        result = format_file_summary(files)
        
        assert "1 file(s) changed" in result
        assert "src/main.py" in result
        assert "+10" in result
        assert "-5" in result
        assert "modified" in result
    
    def test_multiple_files(self):
        """Test formatting multiple files."""
        files = [
            {
                "filename": "file1.py",
                "additions": 5,
                "deletions": 2,
                "status": "modified"
            },
            {
                "filename": "file2.js",
                "additions": 20,
                "deletions": 0,
                "status": "added"
            },
            {
                "filename": "file3.txt",
                "additions": 0,
                "deletions": 10,
                "status": "removed"
            }
        ]
        result = format_file_summary(files)
        
        assert "3 file(s) changed" in result
        assert "file1.py" in result
        assert "file2.js" in result
        assert "file3.txt" in result
        assert "added" in result
        assert "removed" in result
    
    def test_missing_fields(self):
        """Test handling files with missing fields."""
        files = [
            {"filename": "test.py"}  # Missing additions, deletions, status
        ]
        result = format_file_summary(files)
        
        assert "1 file(s) changed" in result
        assert "test.py" in result
        assert "+0" in result
        assert "-0" in result
