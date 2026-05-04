#!/bin/bash
# GitHub Repository Viewer - Portfolio System Architect
# Показывает состояние репозитория прямо в терминале

REPO="Control39/portfolio-system-architect"
BRANCH="main"

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║        📦 GITHUB REPOSITORY VIEWER - PORTFOLIO SYSTEM ARCHITECT    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. ОСНОВНАЯ ИНФОРМАЦИЯ О РЕПОЗИТОРИИ
echo "📊 REPOSITORY INFO:"
echo "─────────────────────────────────────────────────────────────────────"
curl -s "https://api.github.com/repos/$REPO" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"  📛 Name:        {data.get('name', 'N/A')}\")
print(f\"  📝 Description: {data.get('description', 'N/A')[:70]}\")
print(f\"  ⭐ Stars:       {data.get('stargazers_count', 0)}\")
print(f\"  🔱 Forks:       {data.get('forks_count', 0)}\")
print(f\"  👀 Watchers:    {data.get('subscribers_count', 0)}\")
print(f\"  📅 Created:     {data.get('created_at', 'N/A')[:10]}\")
print(f\"  🔄 Updated:     {data.get('updated_at', 'N/A')[:10]}\")
print(f\"  🟢 Status:      {data.get('open_issues_count', 0)} open issues, {data.get('network_count', 0)} forks\")
"
echo ""

# 2. ПОСЛЕДНИЕ КОММИТЫ
echo "📝 LATEST COMMITS:"
echo "─────────────────────────────────────────────────────────────────────"
curl -s "https://api.github.com/repos/$REPO/commits?per_page=5" | python3 -c "
import sys, json
commits = json.load(sys.stdin)
for i, c in enumerate(commits, 1):
    sha = c['sha'][:8]
    msg = c['commit']['message'].split('\n')[0][:60]
    author = c['commit']['author']['name'][:15]
    print(f\"  {i}. {sha} | {author:15} | {msg}\")
"
echo ""

# 3. ВЕТКИ
echo "🌿 BRANCHES:"
echo "─────────────────────────────────────────────────────────────────────"
curl -s "https://api.github.com/repos/$REPO/branches?per_page=10" | python3 -c "
import sys, json
branches = json.load(sys.stdin)
for b in branches[:10]:
    name = b['name']
    last = b['commit']['sha'][:7]
    print(f\"  • {name:<35} ({last})\")
"
echo ""

# 4. ФАЙЛЫ В КОРНЕ
echo "📁 FILES IN ROOT (first 20):"
echo "─────────────────────────────────────────────────────────────────────"
curl -s "https://api.github.com/repos/$REPO/contents" | python3 -c "
import sys, json
files = json.load(sys.stdin)
for f in files[:20]:
    icon = '📁' if f['type'] == 'dir' else '📄'
    print(f\"  {icon} {f['name']:<40}\")
"
echo ""

# 5. README (первые 20 строк)
echo "📖 README.md (first 20 lines):"
echo "─────────────────────────────────────────────────────────────────────"
curl -s "https://raw.githubusercontent.com/$REPO/$BRANCH/README.md" | head -20
echo ""

# 6. ACTION WORKFLOWS (если есть)
echo "⚙️ GITHUB ACTIONS WORKFLOWS:"
echo "─────────────────────────────────────────────────────────────────────"
curl -s "https://api.github.com/repos/$REPO/actions/workflows" | python3 -c "
import sys, json
data = json.load(sys.stdin)
workflows = data.get('workflows', [])
if workflows:
    for w in workflows[:5]:
        name = w['name']
        state = w['state']
        print(f\"  • {name:<30} ({state})\")
else:
    print(\"  ⚠️ No workflows found\")
"
echo ""

# 7. OPEN PULL REQUESTS
echo "🔀 OPEN PULL REQUESTS:"
echo "─────────────────────────────────────────────────────────────────────"
curl -s "https://api.github.com/repos/$REPO/pulls?state=open&per_page=5" | python3 -c "
import sys, json
prs = json.load(sys.stdin)
if prs:
    for pr in prs[:5]:
        num = pr['number']
        title = pr['title'][:50]
        print(f\"  • #{num}: {title}\")
else:
    print(\"  ✅ No open pull requests\")
"
echo ""

# 8. DEPENDABOT VULNERABILITIES
echo "🔒 DEPENDABOT VULNERABILITIES:"
echo "─────────────────────────────────────────────────────────────────────"
curl -s "https://api.github.com/repos/$REPO/dependabot/alerts?per_page=5&state=open" | python3 -c "
import sys, json
alerts = json.load(sys.stdin)
if alerts and len(alerts) > 0:
    for a in alerts[:5]:
        sec = a.get('security_advisory', {})
        print(f\"  • {sec.get('severity', 'unknown')}: {sec.get('summary', 'N/A')[:60]}\")
else:
    print(\"  ✅ No open dependabot alerts\")
" 2>/dev/null || echo "  ⚠️ Cannot fetch alerts (may need auth)"
echo ""

# 9. ЯЗЫКИ (технологии)
echo "🛠️ LANGUAGES USED:"
echo "─────────────────────────────────────────────────────────────────────"
curl -s "https://api.github.com/repos/$REPO/languages" | python3 -c "
import sys, json
langs = json.load(sys.stdin)
total = sum(langs.values())
for lang, bytes_ in sorted(langs.items(), key=lambda x: -x[1])[:5]:
    percent = (bytes_ / total * 100) if total > 0 else 0
    bar = '█' * int(percent / 2) + '░' * (50 - int(percent / 2))
    print(f\"  {lang:12} {bar} {percent:.1f}%\")
"
echo ""

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  🚀 For full details, visit: https://github.com/$REPO              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""