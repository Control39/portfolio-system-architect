---
apply: Always
mode: Agent
---

# 📋 PLAN WORKFLOW

## 🔍 BEFORE WORK
1. Read IMPLEMENTATION_PLAN.md
2. Find next [ ] task by priority (🔴>🟡>🟢)
3. Show user: task #, name, priority, commands
4. Wait for confirmation

## ✅ AFTER COMPLETION
1. Update: [ ] → [x]
2. Add to changelog
3. Commit & push:
   `
   git add IMPLEMENTATION_PLAN.md
   git commit -m "chore: task X.X.X done"
   git push origin main && git push sourcecraft main
   `
4. Show progress + next task

## ➕ ADD TASKS
If user requests:
1. Determine phase & priority
2. Add to plan
3. Update counters
4. Commit & push

## 🚫 RULES
- ✅ ALWAYS read plan first
- ✅ ALWAYS update after
- ✅ ALWAYS commit
- ❌ NO without confirmation

---
**Updated:** 2026-04-28
