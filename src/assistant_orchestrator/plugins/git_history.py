"""Git history plugin for analyzing repository activity.
"""
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def get_stats(root: Path) -> dict[str, Any]:
    """Get Git repository statistics."""
    try:
        # Check if it's a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.warning("Not a git repository")
            return {"error": "Not a git repository"}

        # Get total commits
        total_commits = _get_total_commits(root)

        # Get recent activity (commits in last 30 days)
        recent_commits = _get_recent_commits(root, days=30)

        # Get contributors
        contributors = _get_contributors(root)

        # Get branches
        branches = _get_branches(root)

        logger.info(f"Git stats: {total_commits} commits, {len(contributors)} contributors")

        return {
            "total_commits": total_commits,
            "recent_activity_days": recent_commits,
            "contributors": contributors,
            "branches": branches,
            "is_git_repository": True,
        }
    except Exception as e:
        logger.error(f"Error getting git stats: {e}")
        return {"error": str(e)}


def _run_git_command(root: Path, args: list[str]) -> str:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return ""
    except Exception as e:
        logger.debug(f"Git command failed: {e}")
        return ""


def _get_total_commits(root: Path) -> int:
    """Get total number of commits."""
    output = _run_git_command(root, ["rev-list", "--count", "--all"])
    if output:
        try:
            return int(output)
        except ValueError:
            pass
    return 0


def _get_recent_commits(root: Path, days: int = 30) -> int:
    """Get number of commits in the last N days."""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    output = _run_git_command(root, ["rev-list", "--count", f"--since={since_date}", "--all"])
    if output:
        try:
            return int(output)
        except ValueError:
            pass
    return 0


def _get_contributors(root: Path) -> list[str]:
    """Get list of contributors (authors)."""
    output = _run_git_command(root, ["shortlog", "-s", "-n", "--all"])
    contributors = []
    for line in output.splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            contributors.append(parts[1].strip())
    return contributors[:20]  # Limit to top 20


def _get_branches(root: Path) -> list[str]:
    """Get list of branches."""
    output = _run_git_command(root, ["branch", "-a", "--format=%(refname:short)"])
    branches = [b.strip() for b in output.splitlines() if b.strip()]
    # Filter out remote branches if too many
    local_branches = [b for b in branches if not b.startswith("origin/")]
    return local_branches[:10]  # Limit to 10 branches

