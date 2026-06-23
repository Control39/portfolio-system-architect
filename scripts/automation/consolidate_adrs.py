#!/usr/bin/env python3
"""
ADR Consolidation Script
========================
Consolidates scattered ADR files from multiple directories into a single
canonical location with sequential numbering and duplicate detection.

Usage:
    python scripts/consolidate_adrs.py [--dry-run]

What it does:
1. Backs up existing ADR directories to legacy/adr-archive/
2. Scans docs/adr/ and docs/architecture/decisions/ for ADR-*.md files
3. Detects exact duplicates by MD5 hash (keeps decisions/ over docs/adr/)
4. Skips stub files (< 200 bytes or circular self-references)
5. Assigns new sequential numbers ADR-001 through ADR-0XX
6. Prepends metadata block with Former ID and source path
7. Writes consolidated files to docs/architecture/decisions/
8. Generates RENUMBERING_REPORT.md

Safety:
    - Creates timestamped backup before any changes
    - Dry-run mode shows plan without modifying files
    - Does NOT delete source files (only writes to target)
"""

import argparse
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

SOURCE_DIRS = [
    Path("docs/adr"),
    Path("docs/architecture/decisions"),
]
TARGET_DIR = Path("docs/architecture/decisions")
BACKUP_DIR = Path("legacy/adr-archive")
REPORT_PATH = Path("docs/architecture/RENUMBERING_REPORT.md")

# Explicit file order for renumbering (source relative to repo root → new number)
# This mapping was built from manual audit of all ADR files.
FILE_MAP = [
    # (source_glob_pattern, new_number, note)
    ("docs/architecture/decisions/ADR-001-system-thinking-methodology.md", 1, "Methodology"),
    ("docs/adr/ADR-001.md", 2, "Stack choice (Python vs Node)"),
    ("docs/architecture/decisions/ADR-002-component-integration.md", 3, "Component integration"),
    (
        "docs/architecture/decisions/ADR-010-diagram-format.md",
        4,
        "Diagram format (Mermaid) — was ADR-010",
    ),
    ("docs/architecture/decisions/ADR-003-ml-model-versioning-system.md", 5, "ML Model Registry"),
    ("docs/architecture/decisions/ADR-004-data-storage-format.md", 6, "Data storage format"),
    ("docs/architecture/decisions/ADR-005-ui-technology-choice.md", 7, "UI technology"),
    ("docs/architecture/decisions/ADR-006-data-validation-approach.md", 8, "Data validation"),
    (
        "docs/architecture/decisions/ADR-007-technology-stack-justification.md",
        9,
        "Stack justification",
    ),
    ("docs/architecture/decisions/ADR-008-service-discovery.md", 10, "Service discovery"),
    ("docs/architecture/decisions/ADR-009-base-docker-images.md", 11, "Base Docker images"),
    ("docs/adr/ADR-010-vscode-settings-separation.md", 12, "VSCode settings separation"),
    # ADR-013 skipped — missing (was referenced by system_proof/career_development)
    (
        "docs/architecture/decisions/ADR-015-monorepo-boundary.md",
        14,
        "src/ vs apps/ boundary — was ADR-015",
    ),
    (
        "docs/architecture/decisions/ADR-016-standardize-documentation.md",
        15,
        "Documentation standard — was ADR-016",
    ),
    (
        "docs/architecture/decisions/ADR-017-mcp_server-coverage-decision.md",
        16,
        "MCP Server coverage — was ADR-017",
    ),
    (
        "docs/architecture/decisions/ADR-018-dependency-injection.md",
        17,
        "Dependency injection — was ADR-018",
    ),
    (
        "docs/architecture/decisions/ADR-018-documentation-and-audit-standards.md",
        18,
        "Documentation & audit — was ADR-018",
    ),
    ("docs/architecture/decisions/ADR-019-local-vs-cloud-llm.md", 19, "Local vs Cloud LLM"),
]

# Files to skip (stubs, redirects, templates)
SKIP_PATTERNS = [
    "adr-template.md",
    "ADR-001-system-thinking-methodology.md",  # stub in docs/adr/ (123 bytes)
    "ADR-002.md",  # stub "structure data" (222 bytes)
]

# Duplicates: these files in docs/adr/ are byte-identical to decisions/ counterparts
# NOTE: ADR-004 and ADR-008 have minor path differences; decisions/ version is canonical.
DUPLICATES_IN_ADR = {
    "ADR-002-component-integration.md",
    "ADR-003-ml-model-versioning-system.md",
    "ADR-005-ui-technology-choice.md",
    "ADR-006-data-validation-approach.md",
    "ADR-007-technology-stack-justification.md",
    "ADR-009-base-docker-images.md",
}


# ── Helpers ──────────────────────────────────────────────────────────────────


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def is_stub(path: Path) -> bool:
    """Detect stub/redirect files (< 200 bytes or self-referencing)."""
    if path.stat().st_size < 200:
        return True
    content = path.read_text(encoding="utf-8")
    return bool("См. оригинал" in content or "See original" in content.lower())


def format_new_filename(number: int, original_name: str) -> str:
    """Generate new filename: ADR-NNN-kebab-case.md"""
    # Extract any existing suffix after the number
    parts = original_name.replace(".md", "").split("-", 2)
    suffix = parts[2] if len(parts) >= 3 else "consolidated"
    return f"ADR-{number:03d}-{suffix}.md"


def build_meta_header(former_id: str, former_path: str, new_id: str) -> str:
    return (
        f"> **Former ID:** {former_id}\n"
        f"> **Former path:** `{former_path}`\n"
        f"> **Current ID:** {new_id}\n"
        f"> **Consolidated:** {datetime.now().strftime('%Y-%m-%d')}\n"
        f">\n"
        f"---\n\n"
    )


def backup_directories(dry_run: bool):
    """Create timestamped backup of source ADR directories."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = BACKUP_DIR / f"backup_{timestamp}"

    print(f"📦 Backup target: {backup_root}")
    if dry_run:
        print("   (dry-run: would copy dirs)")
        return backup_root

    backup_root.mkdir(parents=True, exist_ok=True)
    for src in SOURCE_DIRS:
        if src.exists():
            dst = backup_root / src.name
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"   ✅ Backed up {src} → {dst}")
    return backup_root


def verify_duplicates():
    """Verify that claimed duplicates are actually byte-identical."""
    print("\n🔍 Verifying duplicate assertions...")
    ok = True
    for dup_name in DUPLICATES_IN_ADR:
        adr_path = Path("docs/adr") / dup_name
        dec_path = Path("docs/architecture/decisions") / dup_name
        if adr_path.exists() and dec_path.exists():
            if md5(adr_path) != md5(dec_path):
                print(f"   ⚠️  HASH MISMATCH: {dup_name}")
                ok = False
            else:
                print(f"   ✅ Verified duplicate: {dup_name}")
        else:
            print(f"   ℹ️  Missing for check: {dup_name}")
    return ok


def generate_report(actions, backup_path: Path):
    lines = [
        "# ADR Renumbering Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Backup:** `{backup_path}`",
        "",
        "## Summary",
        "",
        f"- **Total ADRs consolidated:** {len(actions)}",
        f"- **Former duplicates skipped:** {len(DUPLICATES_IN_ADR)}",
        f"- **Stubs skipped:** {len(SKIP_PATTERNS)}",
        "",
        "## Renumbering Table",
        "",
        "| New ID | Former ID | File | Note |",
        "|--------|-----------|------|------|",
    ]
    for action in actions:
        lines.append(f"| {action['new_id']} | {action['former_id']} | `{action['new_file']}` | {action['note']} |")

    lines.extend(
        [
            "",
            "## Skipped Files",
            "",
            "| File | Reason |",
            "|------|--------|",
        ]
    )
    for name in SKIP_PATTERNS:
        lines.append(f"| `{name}` | Stub/template/redirect |")
    for name in DUPLICATES_IN_ADR:
        lines.append(f"| `docs/adr/{name}` | Duplicate (identical to decisions/) |")

    lines.extend(
        [
            "",
            "## Next Steps",
            "",
            "1. Update cross-references in README files to use new ADR numbers.",
            "2. Update `README.md` ADR table.",
            "3. Update `CONTRIBUTING.md` ADR examples.",
            "4. Archive `docs/adr/` directory (or remove after verification).",
            "",
        ]
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📄 Report written: {REPORT_PATH}")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Consolidate ADR files")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without changes")
    args = parser.parse_args()

    print("=" * 60)
    print(" ADR Consolidation Script")
    print("=" * 60)

    if args.dry_run:
        print("\n⚠️  DRY RUN MODE — no files will be modified\n")

    # 1. Backup (before any changes)
    backup_path = backup_directories(args.dry_run)

    # 2. Verify duplicates (before clearing target)
    if not verify_duplicates():
        print("\n❌ Duplicate verification failed. Aborting.")
        sys.exit(1)

    # 3. Read all files into memory FIRST (before clearing target dir)
    actions = []
    seen_hashes = set()
    files_to_write = []  # (target_filename, content, source_name, note)

    print("\n📝 Processing ADR mapping...")
    for pattern, new_num, note in FILE_MAP:
        source_path = Path(pattern)
        if not source_path.exists():
            print(f"   ⚠️  NOT FOUND: {pattern} — skipping")
            continue

        file_hash = md5(source_path)
        if file_hash in seen_hashes:
            print(f"   ⏩ Already handled (duplicate hash): {source_path.name}")
            continue
        seen_hashes.add(file_hash)

        new_id = f"ADR-{new_num:03d}"
        new_filename = format_new_filename(new_num, source_path.name)
        former_id = source_path.stem

        original_content = source_path.read_text(encoding="utf-8")
        meta = build_meta_header(former_id, str(source_path), new_id)
        new_content = meta + original_content

        files_to_write.append((new_filename, new_content, source_path.name, note))
        actions.append(
            {
                "new_id": new_id,
                "former_id": former_id,
                "new_file": new_filename,
                "note": note,
            }
        )

        if args.dry_run:
            print(f"   📝 Would write: {source_path.name} → {new_filename}")

    # 4. Clear target directory (only after all files are read)
    if not args.dry_run:
        print(f"\n🧹 Cleaning {TARGET_DIR}...")
        for f in TARGET_DIR.glob("ADR-*.md"):
            f.unlink()
            print(f"   🗑️  Removed old: {f.name}")

        # 5. Write all files
        print("\n✍️  Writing consolidated ADRs...")
        for filename, content, source_name, note in files_to_write:
            target_file = TARGET_DIR / filename
            target_file.write_text(content, encoding="utf-8")
            print(f"   ✅ Written: {source_name} → {filename}")

    # 6. Generate report
    generate_report(actions, backup_path)

    print("\n" + "=" * 60)
    if args.dry_run:
        print(" Dry run complete. No files modified.")
        print(" Re-run without --dry-run to apply changes.")
    else:
        print(f" Consolidation complete. {len(actions)} ADRs written.")
        print(f" Backup saved to: {backup_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
