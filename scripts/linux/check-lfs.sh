#!/bin/bash
# check-lfs.sh: Git LFS integrity check for CI/pre-commit
# Usage: ./scripts/check-lfs.sh [all|tracked|staged]

set -e

echo "🔍 Checking Git LFS files..."

if [ "$1" = "staged" ]; then
  git diff --cached --name-only --diff-filter=ACM | grep -E '\.(png|jpg|jpeg|gif|pdf|zip|tar|bin)$' | while read file; do
    if [ -f "$file" ]; then
      if ! git lfs ls-files "$file" > /dev/null 2>&1; then
        echo "❌ $file not tracked by LFS but should be (large/binary)"
        exit 1
      fi
    fi
  done
elif [ "$1" = "tracked" ]; then
  git lfs ls-files | while read hash file; do
    if [ ! -f "$file" ]; then
      echo "❌ LFS file missing: $file"
      exit 1
    fi
    if ! git lfs pointer --file="$file" --check; then
      echo "❌ LFS pointer corrupt: $file"
      exit 1
    fi
  done
else  # all/default
  ./scripts/check-lfs.sh tracked
  ./scripts/check-lfs.sh staged
fi

git lfs prune --dry-run | grep -q "would free" && echo "ℹ️ Prunable LFS objects found" || echo "✅ No orphaned LFS"

echo "✅ LFS check passed"
