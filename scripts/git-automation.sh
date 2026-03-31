#!/bin/bash

# Git automation script for portfolio-system-architect
# Automates versioning, tagging, and changelog updates

set -e

echo "🔧 Git Automation Script"
echo "================================================================"

# Function to show usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  version     Create new version and tag"
    echo "  changelog   Update CHANGELOG.md from git history"
    echo "  release     Create release (version + changelog + tag)"
    echo "  hooks       Install Git hooks"
    echo "  status      Show Git status and pending changes"
    echo ""
    echo "Examples:"
    echo "  $0 version patch     # Bump patch version (0.1.0 → 0.1.1)"
    echo "  $0 version minor     # Bump minor version (0.1.0 → 0.2.0)"
    echo "  $0 version major     # Bump major version (0.1.0 → 1.0.0)"
    echo "  $0 release minor     # Create release with minor version bump"
}

# Function to get current version from pyproject.toml
get_current_version() {
    if [ -f "pyproject.toml" ]; then
        grep -E '^version =' pyproject.toml | sed -E 's/version = "([^"]+)"/\1/' | head -1
    elif [ -f "__version__.py" ]; then
        grep -E '__version__' __version__.py | sed -E "s/.*= '([^']+)'.*/\1/"
    else
        echo "0.1.0"  # Default version
    fi
}

# Function to bump version
bump_version() {
    local version=$1
    local bump_type=$2
    
    IFS='.' read -r major minor patch <<< "$version"
    
    case $bump_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "❌ Invalid bump type: $bump_type"
            echo "   Use: major, minor, or patch"
            exit 1
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Function to update version in files
update_version_files() {
    local new_version=$1
    
    echo "📝 Updating version to $new_version..."
    
    # Update pyproject.toml
    if [ -f "pyproject.toml" ]; then
        sed -i.bak -E "s/^version = \".*\"/version = \"$new_version\"/" pyproject.toml
        rm -f pyproject.toml.bak
        echo "  ✅ Updated pyproject.toml"
    fi
    
    # Update __version__.py if exists
    if [ -f "src/__version__.py" ]; then
        sed -i.bak -E "s/__version__ = \".*\"/__version__ = \"$new_version\"/" src/__version__.py
        rm -f src/__version__.py.bak
        echo "  ✅ Updated src/__version__.py"
    fi
    
    # Update package.json if exists
    if [ -f "package.json" ]; then
        sed -i.bak -E "s/\"version\": \".*\"/\"version\": \"$new_version\"/" package.json
        rm -f package.json.bak
        echo "  ✅ Updated package.json"
    fi
}

# Function to generate changelog
generate_changelog() {
    echo "📋 Generating changelog..."
    
    # Check if git-changelog is available
    if command -v git-changelog &> /dev/null; then
        git-changelog -o CHANGELOG.md
        echo "  ✅ Generated CHANGELOG.md using git-changelog"
    else
        # Simple changelog generation using git log
        echo "# Changelog" > CHANGELOG.md.new
        echo "" >> CHANGELOG.md.new
        echo "## [Unreleased]" >> CHANGELOG.md.new
        echo "" >> CHANGELOG.md.new
        
        # Get commits since last tag
        last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
        if [ -n "$last_tag" ]; then
            echo "### Added" >> CHANGELOG.md.new
            git log --oneline --no-merges "$last_tag..HEAD" --grep="^feat" | sed 's/^/- /' >> CHANGELOG.md.new
            echo "" >> CHANGELOG.md.new
            echo "### Changed" >> CHANGELOG.md.new
            git log --oneline --no-merges "$last_tag..HEAD" --grep="^chore\|^refactor\|^style" | sed 's/^/- /' >> CHANGELOG.md.new
            echo "" >> CHANGELOG.md.new
            echo "### Fixed" >> CHANGELOG.md.new
            git log --oneline --no-merges "$last_tag..HEAD" --grep="^fix" | sed 's/^/- /' >> CHANGELOG.md.new
        else
            echo "  ⚠️  No previous tag found. Creating initial changelog."
            echo "### Initial release" >> CHANGELOG.md.new
        fi
        
        # Append existing changelog if it exists
        if [ -f "CHANGELOG.md" ]; then
            tail -n +2 CHANGELOG.md >> CHANGELOG.md.new
        fi
        
        mv CHANGELOG.md.new CHANGELOG.md
        echo "  ✅ Generated CHANGELOG.md from git history"
    fi
}

# Function to create Git tag
create_git_tag() {
    local version=$1
    
    echo "🏷️  Creating Git tag v$version..."
    
    # Check if tag already exists
    if git rev-parse "v$version" >/dev/null 2>&1; then
        echo "  ⚠️  Tag v$version already exists"
        return
    fi
    
    # Create annotated tag
    git tag -a "v$version" -m "Release v$version"
    echo "  ✅ Created tag v$version"
    
    # Show tag info
    echo ""
    echo "Tag created successfully:"
    git show "v$version" --stat
}

# Function to install Git hooks
install_git_hooks() {
    echo "🔗 Installing Git hooks..."
    
    # Create hooks directory if it doesn't exist
    mkdir -p .git/hooks
    
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for portfolio-system-architect

echo "🔍 Running pre-commit checks..."

# Run pre-commit if available
if command -v pre-commit &> /dev/null; then
    pre-commit run --all-files
    if [ $? -ne 0 ]; then
        echo "❌ Pre-commit checks failed. Please fix the issues before committing."
        exit 1
    fi
fi

echo "✅ Pre-commit checks passed"
EOF
    
    chmod +x .git/hooks/pre-commit
    echo "  ✅ Installed pre-commit hook"
    
    # Prepare-commit-msg hook (for conventional commits)
    cat > .git/hooks/prepare-commit-msg << 'EOF'
#!/bin/bash
# Prepare-commit-msg hook for conventional commits

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# Only add template for new commits, not for merges, amends, etc.
if [ "$COMMIT_SOURCE" = "message" ] || [ "$COMMIT_SOURCE" = "template" ]; then
    cat << 'TEMPLATE'

# Please enter the commit message for your changes.
# Lines starting with '#' will be ignored.
#
# Conventional commit types:
# feat:     A new feature
# fix:      A bug fix
# docs:     Documentation only changes
# style:    Changes that do not affect the meaning of the code
# refactor: A code change that neither fixes a bug nor adds a feature
# perf:     A code change that improves performance
# test:     Adding missing tests or correcting existing tests
# chore:    Changes to the build process or auxiliary tools
#
# Example: feat: add user authentication system
TEMPLATE
fi
EOF
    
    chmod +x .git/hooks/prepare-commit-msg
    echo "  ✅ Installed prepare-commit-msg hook"
    
    echo ""
    echo "Git hooks installed successfully!"
}

# Function to show Git status
show_git_status() {
    echo "📊 Git Status Overview"
    echo "======================"
    
    # Current branch
    echo "Current branch: $(git branch --show-current)"
    
    # Status
    echo ""
    echo "Changes:"
    git status --short
    
    # Staged changes
    echo ""
    echo "Staged changes (diff --cached):"
    git diff --cached --stat || echo "  No staged changes"
    
    # Recent commits
    echo ""
    echo "Recent commits:"
    git log --oneline -5
    
    # Tags
    echo ""
    echo "Latest tags:"
    git tag --sort=-version:refname | head -5
}

# Main script logic
case "${1:-help}" in
    version)
        if [ -z "$2" ]; then
            echo "❌ Please specify version bump type: patch, minor, or major"
            exit 1
        fi
        
        current_version=$(get_current_version)
        new_version=$(bump_version "$current_version" "$2")
        
        echo "🔄 Bumping version: $current_version → $new_version"
        update_version_files "$new_version"
        
        # Commit version change
        git add pyproject.toml src/__version__.py package.json 2>/dev/null || true
        git commit -m "chore: bump version to $new_version"
        
        create_git_tag "$new_version"
        
        echo ""
        echo "✅ Version updated to $new_version and tagged"
        ;;
    
    changelog)
        generate_changelog
        git add CHANGELOG.md
        git commit -m "docs: update changelog" || echo "  ⚠️  No changes to commit"
        echo "✅ Changelog updated"
        ;;
    
    release)
        if [ -z "$2" ]; then
            echo "❌ Please specify version bump type: patch, minor, or major"
            exit 1
        fi
        
        echo "🚀 Creating release..."
        
        # Run tests first
        echo "1. Running tests..."
        make test || { echo "❌ Tests failed. Aborting release."; exit 1; }
        
        # Bump version
        echo "2. Bumping version..."
        current_version=$(get_current_version)
        new_version=$(bump_version "$current_version" "$2")
        update_version_files "$new_version"
        
        # Generate changelog
        echo "3. Generating changelog..."
        generate_changelog
        
        # Commit changes
        echo "4. Committing release..."
        git add .
        git commit -m "chore(release): v$new_version"
        
        # Create tag
        echo "5. Creating tag..."
        create_git_tag "$new_version"
        
        echo ""
        echo "🎉 Release v$new_version created successfully!"
        echo ""
        echo "Next steps:"
        echo "1. Review changes: git log --oneline -5"
        echo "2. Push tags: git push --tags"
        echo "3. Push changes: git push"
        echo "4. Create GitHub release from tag v$new_version"
        ;;
    
    hooks)
        install_git_hooks
        ;;
    
    status)
        show_git_status
        ;;
    
    help|--help|-h)
        usage
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        usage
        exit 1
        ;;
esac

echo ""
echo "================================================================"