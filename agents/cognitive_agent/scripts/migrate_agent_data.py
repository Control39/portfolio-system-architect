#!/usr/bin/env python3
"""
Migration script: Move agent runtime data from apps/cognitive_agent/ to .agent_data/

This script safely migrates all runtime data from the old location to the new
hidden directory structure.
"""

import shutil
from pathlib import Path


def migrate_directory(src: Path, dst: Path, name: str):
    """Migrate a single subdirectory"""
    if not src.exists():
        print(f"⚠️  {name}: Source directory does not exist: {src}")
        return False

    if not dst.exists():
        dst.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dst}")

    # Copy contents
    try:
        for item in src.iterdir():
            if item.is_dir():
                dst_item = dst / item.name
                if dst_item.exists():
                    print(f"  ⚠️  Skipping existing: {dst_item}")
                else:
                    shutil.copytree(item, dst_item)
                    print(f"  ✅ Copied directory: {item.name}")
            else:
                dst_item = dst / item.name
                if not dst_item.exists():
                    shutil.copy2(item, dst_item)
                    print(f"  ✅ Copied file: {item.name}")
                else:
                    print(f"  ⚠️  Skipping existing file: {item.name}")

        print(f"✅ Migrated: {name}")
        return True
    except Exception as e:
        print(f"❌ Error migrating {name}: {e}")
        return False


def main():
    """Main migration function"""
    # repo_root is c:\repo (3 levels up from scripts/)
    repo_root = Path(__file__).parent.parent.parent.parent
    old_base = repo_root / "apps" / "cognitive_agent"
    new_base = repo_root / "agents" / "cognitive_agent" / ".agent_data"

    print("=" * 70)
    print("Cognitive Agent Data Migration")
    print("=" * 70)
    print(f"Source: {old_base}")
    print(f"Target: {new_base}")
    print("=" * 70)
    print()

    if not old_base.exists():
        print("❌ Old directory does not exist. Nothing to migrate.")
        print("   The new structure is already in place.")
        return

    # Ensure new base exists
    new_base.mkdir(parents=True, exist_ok=True)

    # Define directory mappings
    directories = [
        ("logs", "logs"),
        ("reports", "reports"),
        ("scans", "scans"),
        ("config", "config"),
        ("data", "data"),
        ("status", "status"),
        ("plans", "plans"),
    ]

    migrated_count = 0
    total_count = len(directories)

    for src_name, dst_name in directories:
        src_dir = old_base / src_name
        dst_dir = new_base / dst_name

        if src_dir.exists():
            print(f"\nMigrating: {src_name} → {dst_name}")
            print("-" * 50)
            if migrate_directory(src_dir, dst_dir, src_name):
                migrated_count += 1
        else:
            print(f"⊘  Skipping {src_name}: does not exist in source")

    print("\n" + "=" * 70)
    print(f"Migration Complete: {migrated_count}/{total_count} directories migrated")
    print("=" * 70)

    if migrated_count > 0:
        print("\n✅ Next steps:")
        print("   1. Verify the migrated data in .agent_data/")
        print("   2. Test that the agent works correctly")
        print("   3. You can now safely delete apps/cognitive_agent/")
        print("\n   To delete old directory:")
        print(f"   rm -rf {old_base}")
    else:
        print("\nℹ️  No data was migrated. The old directory may be empty.")


if __name__ == "__main__":
    main()
