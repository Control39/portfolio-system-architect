"""Molecule test orchestrator.

Runs pytest for each molecule (apps/*/tests) in isolation.

Design constraints (composition architecture):
- No shim packages
- No sys.modules import hacks
- No global PYTHONPATH mutation
- Each molecule can provide its own local conftest.py for import roots

Outputs a markdown health report under docs/reports.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"
REPORT_DIR = REPO_ROOT / "docs" / "reports"


@dataclass(frozen=True)
class MoleculeResult:
    name: str
    path: Path
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _iter_molecules() -> List[Path]:
    if not APPS_DIR.exists():
        return []
    molecules: List[Path] = []
    for app_dir in sorted(APPS_DIR.iterdir()):
        if not app_dir.is_dir():
            continue
        tests_dir = app_dir / "tests"
        if tests_dir.exists():
            molecules.append(app_dir)
    return molecules


def _run_pytest_for_molecule(molecule_dir: Path) -> MoleculeResult:
    tests_dir = molecule_dir / "tests"

    # Run with cwd=molecule_dir so local conftest.py and relative imports behave correctly.
    # Keep output short; still capture full stdout/stderr for report snippets.
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(tests_dir),
            "-q",
            "--tb=short",
        ],
        cwd=str(molecule_dir),
        capture_output=True,
        text=True,
        env=None,
    )

    return MoleculeResult(
        name=molecule_dir.name,
        path=molecule_dir,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def _summarize_for_report(out: str, err: str, max_chars: int = 1200) -> str:
    text = (out + "\n" + err).strip()
    if not text:
        return "(no output)"

    # Prefer error blocks if present.
    # Keep it deterministic-ish: take first chunk up to max_chars.
    if len(text) > max_chars:
        return text[: max_chars - 3] + "..."
    return text


def _generate_report(results: List[MoleculeResult], timestamp: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"services_health_{timestamp}.md"

    passing = sum(1 for r in results if r.ok)
    total = len(results)
    failing = total - passing

    lines: List[str] = []
    lines.append("# Services Health Report (Compositional Architecture)\n")
    lines.append(f"**Generated:** {datetime.now().isoformat()}\n")
    lines.append(f"**Total molecules with tests:** {total}")
    lines.append(f"- ✅ Passing: {passing}")
    lines.append(f"- ❌ Failing: {failing}\n")

    lines.append("## Detailed\n")

    for r in sorted(results, key=lambda x: x.name):
        status = "✅" if r.ok else "❌"
        lines.append(f"### {status} {r.name} ({r.path})")
        lines.append("")
        lines.append("```")
        lines.append(_summarize_for_report(r.stdout, r.stderr))
        lines.append("```")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main(argv: Optional[List[str]] = None) -> int:
    _ = argv

    molecules = _iter_molecules()
    if not molecules:
        print("No molecules found under apps/*/tests")
        return 0

    print(f"Found {len(molecules)} molecules with tests")

    results: List[MoleculeResult] = []

    for mol in molecules:
        print(f"Testing {mol.name}...")
        res = _run_pytest_for_molecule(mol)
        results.append(res)
        print(f"  -> {'PASS' if res.ok else 'FAIL'} (code={res.returncode})")

    timestamp = datetime.now().strftime("%Y-%m-%d")
    report_path = _generate_report(results, timestamp)

    print(f"\nReport: {report_path}")

    # Non-zero exit if any molecule failed
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

