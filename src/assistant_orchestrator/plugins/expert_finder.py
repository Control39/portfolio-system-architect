"""
Expert finder plugin for identifying domain experts in the codebase.
"""

import logging
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ExpertFinder:
    """Find experts based on git history analysis."""

    def __init__(self, project_root: Path):
        self.root = project_root.resolve()

    def find_experts_by_module(self, min_commits: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Find experts for each module based on git blame and commit history."""
        try:
            # Check if it's a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=False,
            )  # nosec: safe command with hardcoded arguments
            if result.returncode != 0:
                logger.warning("Not a git repository, cannot find experts")
                return {}

            # Get list of source files
            source_files = self._get_source_files()

            experts_by_module = defaultdict(list)

            for file in source_files[:50]:  # Limit to 50 files for performance
                module = self._extract_module_name(file)
                file_experts = self._analyze_file_experts(file, min_commits)

                if file_experts:
                    experts_by_module[module].extend(file_experts)

            # Deduplicate and rank experts per module
            ranked_experts = {}
            for module, experts in experts_by_module.items():
                ranked = self._rank_experts(experts)
                ranked_experts[module] = ranked[:5]  # Top 5 experts per module

            logger.info(f"Found experts for {len(ranked_experts)} modules")
            return dict(ranked_experts)

        except Exception as e:
            logger.error(f"Error finding experts: {e}")
            return {}

    def find_bottlenecks(self) -> Dict[str, Any]:
        """Identify potential bottlenecks (single points of failure)."""
        try:
            # Get contributor statistics
            contributors = self._get_contributor_stats()

            if not contributors:
                return {}

            total_commits = sum(c["commits"] for c in contributors)
            if total_commits == 0:
                return {}

            # Find contributors with disproportionate contribution
            bottlenecks = []
            for contributor in contributors:
                percentage = (contributor["commits"] / total_commits) * 100
                if percentage > 50:  # More than 50% of commits
                    bottlenecks.append(
                        {
                            "contributor": contributor["name"],
                            "percentage": round(percentage, 1),
                            "modules": contributor.get("modules", []),
                            "risk": "high",
                            "recommendation": "Consider knowledge sharing and cross-training",
                        }
                    )

            # Find modules with single expert
            module_experts = self.find_experts_by_module(min_commits=1)
            single_expert_modules = []
            for module, experts in module_experts.items():
                if len(experts) == 1:
                    single_expert_modules.append(
                        {
                            "module": module,
                            "expert": experts[0]["name"],
                            "commits": experts[0]["commits"],
                            "risk": "medium",
                            "recommendation": "Add at least one more contributor to this module",
                        }
                    )

            return {
                "bottlenecks": bottlenecks,
                "single_expert_modules": single_expert_modules[:10],
                "total_contributors": len(contributors),
                "total_commits": total_commits,
            }

        except Exception as e:
            logger.error(f"Error finding bottlenecks: {e}")
            return {}

    def _get_source_files(self) -> List[Path]:
        """Get list of source files in the repository."""
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )  # nosec: safe command with hardcoded arguments

            if result.returncode == 0:
                files = [
                    Path(line.strip())
                    for line in result.stdout.splitlines()
                    if line.strip() and self._is_source_file(line.strip())
                ]
                return files
        except Exception as e:
            logger.debug(f"Error getting source files: {e}")

        return []

    def _is_source_file(self, filename: str) -> bool:
        """Check if file is a source code file."""
        source_extensions = {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".go",
            ".rs",
            ".cpp",
            ".c",
            ".cs",
            ".php",
        }
        return Path(filename).suffix.lower() in source_extensions

    def _extract_module_name(self, filepath: Path) -> str:
        """Extract module name from file path."""
        # Try to find the most meaningful directory
        parts = filepath.parts

        # Look for common source directories
        for i, part in enumerate(parts):
            if part in {"src", "app", "apps", "lib", "packages"} and i + 1 < len(parts):
                return "/".join(parts[i : i + 2])

        # Fallback to first two parts or filename
        if len(parts) >= 2:
            return "/".join(parts[:2])
        return str(filepath)

    def _analyze_file_experts(self, filepath: Path, min_commits: int) -> List[Dict[str, Any]]:
        """Analyze git blame to find experts for a specific file."""
        try:
            # Get git blame output
            result = subprocess.run(
                ["git", "blame", "--line-porcelain", str(filepath)],
                cwd=self.root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )  # nosec: safe command with hardcoded arguments

            if result.returncode != 0:
                return []

            # Parse blame output to count contributions per author
            author_counts = defaultdict(int)
            current_author = None

            for line in result.stdout.splitlines():
                if line.startswith("author "):
                    current_author = line[7:].strip()
                elif line.startswith("author-mail "):
                    # Count this line for the current author
                    if current_author:
                        author_counts[current_author] += 1

            # Convert to expert list
            experts = []
            total_lines = sum(author_counts.values())

            for author, lines in author_counts.items():
                if lines >= min_commits:  # Use lines as proxy for contribution
                    percentage = (lines / total_lines) * 100 if total_lines > 0 else 0
                    experts.append(
                        {
                            "name": author,
                            "lines": lines,
                            "percentage": round(percentage, 1),
                            "file": str(filepath),
                        }
                    )

            return experts

        except Exception as e:
            logger.debug(f"Error analyzing file {filepath}: {e}")
            return []

    def _rank_experts(self, experts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank experts by contribution level."""
        # Group by name across multiple files
        expert_contributions = defaultdict(lambda: {"lines": 0, "files": set(), "details": []})

        for expert in experts:
            name = expert["name"]
            expert_contributions[name]["lines"] += expert["lines"]
            expert_contributions[name]["files"].add(expert["file"])
            expert_contributions[name]["details"].append(expert)

        # Convert to ranked list
        ranked = []
        for name, data in expert_contributions.items():
            ranked.append(
                {
                    "name": name,
                    "total_lines": data["lines"],
                    "file_count": len(data["files"]),
                    "files": list(data["files"])[:3],  # Top 3 files
                    "details": data["details"][:3],
                }
            )

        # Sort by total lines (descending)
        ranked.sort(key=lambda x: x["total_lines"], reverse=True)
        return ranked

    def _get_contributor_stats(self) -> List[Dict[str, Any]]:
        """Get contributor statistics from git log."""
        try:
            # Get commit count per author
            result = subprocess.run(
                ["git", "shortlog", "-s", "-n", "--all"],
                cwd=self.root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )  # nosec: safe command with hardcoded arguments

            if result.returncode != 0:
                return []

            contributors = []
            for line in result.stdout.splitlines():
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    commits = int(parts[0].strip())
                    name = parts[1].strip()
                    contributors.append(
                        {
                            "name": name,
                            "commits": commits,
                            "modules": [],  # Would need more analysis
                        }
                    )

            return contributors

        except Exception as e:
            logger.debug(f"Error getting contributor stats: {e}")
            return []


def find_experts(root: Path) -> Dict[str, Any]:
    """Public interface for expert finding."""
    finder = ExpertFinder(root)
    experts = finder.find_experts_by_module()
    bottlenecks = finder.find_bottlenecks()

    return {
        "module_experts": experts,
        "bottlenecks": bottlenecks,
        "summary": {
            "total_modules_with_experts": len(experts),
            "total_bottlenecks": len(bottlenecks.get("bottlenecks", [])),
            "single_expert_modules": len(bottlenecks.get("single_expert_modules", [])),
        },
    }
