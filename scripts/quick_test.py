"""Minimal molecule health check (composition architecture).

Runs pytest for each apps/*/tests directory in isolation.
No shim packages, no sys.modules hacks, no global PYTHONPATH mutations.

Outputs per-molecule PASS/FAIL and a small snippet of stderr.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def iter_molecule_tests(repo_root: Path):
    apps_dir = repo_root / "apps"
    if not apps_dir.exists():
        return
    for app_dir in sorted(apps_dir.iterdir()):
        if not app_dir.is_dir():
            continue
        tests_dir = app_dir / "tests"
        if tests_dir.exists() and tests_dir.is_dir():
            yield app_dir.name, tests_dir


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    print("=== MOLECULE HEALTH CHECK ===\n")

    results: list[tuple[str, int]] = []

    for name, tests_dir in iter_molecule_tests(repo_root):
        print(f"🔬 Testing {name}...", end=" ", flush=True)

        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(tests_dir),
                "-q",
                "--tb=line",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )

        results.append((name, proc.returncode))

        if proc.returncode == 0:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            # show a few failure lines
            lines = [l for l in (proc.stdout + "\n" + proc.stderr).splitlines() if l.strip()]
            # prefer 'FAIL' lines
            fail_lines = [l for l in lines if "FAIL" in l or "ERROR" in l]
            for l in (fail_lines[:3] or lines[:3]):
                print("     └─ " + l[:200])

    failing = [n for (n, rc) in results if rc != 0]
    if failing:
        print(f"\nFAILED MOLECULES ({len(failing)}): {', '.join(failing)}")
        return 1

    print("\n=== DONE (all passed) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

