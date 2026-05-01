"""Base check classes for repository audit."""

import abc
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class CheckResult:
    """Result of a single check."""

    def __init__(
        self,
        check_id: str,
        description: str,
        status: str,  # "PASS", "FAIL", "WARNING", "ERROR", "SKIP"
        details: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
        weight: float = 1.0,
        category: str = "uncategorized",
    ):
        self.check_id = check_id
        self.description = description
        self.status = status
        self.details = details
        self.path = str(path) if path else None
        self.weight = weight
        self.category = category

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.check_id,
            "description": self.description,
            "status": self.status,
            "details": self.details,
            "path": self.path,
            "weight": self.weight,
            "category": self.category,
        }

    def __repr__(self):
        return f"<CheckResult {self.check_id}: {self.status}>"


class BaseCheck(abc.ABC):
    """Abstract base class for a repository check."""

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path).resolve()
        self.results: List[CheckResult] = []

    @property
    @abc.abstractmethod
    def check_id(self) -> str:
        """Unique identifier for the check."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Human‑readable description."""
        pass

    @property
    def category(self) -> str:
        """Category of the check (e.g., 'security', 'documentation')."""
        return "uncategorized"

    @property
    def weight(self) -> float:
        """Weight of this check in scoring (default 1.0)."""
        return 1.0

    @abc.abstractmethod
    def run(self) -> List[CheckResult]:
        """Execute the check and return results."""
        pass

    def _add_result(
        self,
        status: str,
        details: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
    ) -> CheckResult:
        """Helper to create and store a result."""
        result = CheckResult(
            check_id=self.check_id,
            description=self.description,
            status=status,
            details=details,
            path=path,
            weight=self.weight,
            category=self.category,
        )
        self.results.append(result)
        return result

    def check_file_exists(self, relative_path: str) -> bool:
        """Check if a file exists."""
        full_path = self.repo_path / relative_path
        exists = full_path.exists()
        if exists:
            self._add_result("PASS", f"File exists: {relative_path}", relative_path)
        else:
            self._add_result("FAIL", f"File missing: {relative_path}", relative_path)
        return exists

    def check_directory_exists(self, relative_path: str) -> bool:
        """Check if a directory exists."""
        full_path = self.repo_path / relative_path
        exists = full_path.is_dir()
        if exists:
            self._add_result("PASS", f"Directory exists: {relative_path}", relative_path)
        else:
            self._add_result("FAIL", f"Directory missing: {relative_path}", relative_path)
        return exists

    def check_file_content(
        self, relative_path: str, keyword: str, description: Optional[str] = None
    ) -> bool:
        """Check if file contains a keyword."""
        full_path = self.repo_path / relative_path
        if not full_path.exists():
            self._add_result(
                "FAIL",
                f"File missing for content check: {relative_path}",
                relative_path,
            )
            return False
        try:
            content = full_path.read_text(encoding="utf-8")
            if keyword in content:
                self._add_result(
                    "PASS",
                    f"Keyword '{keyword}' found in {relative_path}",
                    relative_path,
                )
                return True
            else:
                self._add_result(
                    "FAIL",
                    f"Keyword '{keyword}' not found in {relative_path}",
                    relative_path,
                )
                return False
        except Exception as e:
            self._add_result(
                "ERROR",
                f"Error reading {relative_path}: {e}",
                relative_path,
            )
            return False


class RepositoryAuditor:
    """Main auditor that runs a collection of checks."""

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path).resolve()
        self.checks: List[BaseCheck] = []
        self.results: List[CheckResult] = []

    def register_check(self, check_class: type) -> None:
        """Register a check class (instantiated with repo_path)."""
        self.checks.append(check_class(self.repo_path))

    def run_all(self) -> List[CheckResult]:
        """Run all registered checks and collect results."""
        self.results = []
        for check in self.checks:
            try:
                check_results = check.run()
                self.results.extend(check_results)
            except Exception as e:
                self.results.append(
                    CheckResult(
                        check_id=check.check_id,
                        description=check.description,
                        status="ERROR",
                        details=f"Check crashed: {e}",
                        category=check.category,
                    )
                )
        return self.results

    def score(self) -> Dict[str, Any]:
        """Calculate overall score."""
        if not self.results:
            return {"total": 0, "score": 0, "percentage": 0.0}

        total_weight = 0.0
        earned_weight = 0.0
        by_category: Dict[str, Dict[str, float]] = {}

        for r in self.results:
            if r.status in ("PASS", "WARNING"):
                earned_weight += r.weight
            total_weight += r.weight

            # Aggregate by category
            cat = r.category
            if cat not in by_category:
                by_category[cat] = {"total": 0.0, "earned": 0.0}
            by_category[cat]["total"] += r.weight
            if r.status in ("PASS", "WARNING"):
                by_category[cat]["earned"] += r.weight

        percentage = (earned_weight / total_weight * 100) if total_weight > 0 else 0.0

        category_scores = {}
        for cat, data in by_category.items():
            cat_pct = (data["earned"] / data["total"] * 100) if data["total"] > 0 else 0.0
            category_scores[cat] = {
                "score": data["earned"],
                "total": data["total"],
                "percentage": round(cat_pct, 2),
            }

        return {
            "total": total_weight,
            "score": earned_weight,
            "percentage": round(percentage, 2),
            "by_category": category_scores,
        }

    def report(self, format: str = "console") -> str:
        """Generate a report."""
        score = self.score()
        if format == "json":
            data = {
                "score": score,
                "results": [r.to_dict() for r in self.results],
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        # Default console format
        lines = [
            "Repository Audit Report",
            f"Path: {self.repo_path}",
            f"Total checks: {len(self.results)}",
            f"Overall score: {score['score']:.1f}/{score['total']:.1f} ({score['percentage']:.2f}%)",
            "",
            "Category breakdown:",
        ]
        for cat, cat_score in score["by_category"].items():
            lines.append(
                f"  {cat}: {cat_score['score']:.1f}/{cat_score['total']:.1f} ({cat_score['percentage']:.2f}%)"
            )
        lines.append("")
        lines.append("Detailed results:")
        for r in self.results:
            lines.append(f"  [{r.status}] {r.description} ({r.path or 'N/A'})")
            if r.details:
                lines.append(f"      {r.details}")
        return "\n".join(lines)
