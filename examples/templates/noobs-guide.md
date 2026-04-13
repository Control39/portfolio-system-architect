# Noobs Guide: Replicate My Zero→Architect Journey
*Social impact: Empower non-tech to build like me. Paste into your repo. Addresses 'scalability for others'.*

## Step 0: Mindset
- You're not coder — you're architect.
- AI = tool; you = director.
- Goal: Evidence ecosystem, not perfect code.

## Step 1: Setup (5min)
```bash
git clone https://github.com/leadarchitect-ai/portfolio-system-architect.git my-journey
cd my-journey
docker compose up -d  # IT-Compass UI: localhost:8501
```

## Step 2: Track Markers (Daily, 15min)
- Open IT-Compass.
- Log skills: 'systemic thinking' → auto RAG evidence.
- Reject AI suggestions per human-decisions.md examples.

## Step 3: Iterate Workflow
Follow [human-ai-workflow.md](../05_DOCUMENTATION/human-ai-workflow.md):
1. Goal: 'My career markers'.
2. AI gen → You eval/reject.
3. Document decision.
4. Docker rebuild.

## Step 4: Build Evidence
- Add your cases to `03_CASES/evolution-cases/`.
- Metrics: Run BENCHMARK_SUITE/test_metrics.py.
- One-pager: Copy grants/one-pager.md, customize.

## Step 5: Portfolio Auto-Gen
- `docker compose exec it-compass python src/portfolio_gen.py`
- Git commit: Your proof generated.

## Tips from Me (3yr Journey)
- 80% time save: Focus decisions, not code.
- Skeptics? Point to human-decisions.md.
- Scale: Apply to your domain (teaching/marketing).

## Metrics You'll See
- Prototyping: 3w→3d.
- Confidence: From zero to grant-ready.

**Fork, adapt, share! #CognitiveArchitect** `leadarchitect@yandex.ru`

*Template v1.0. MIT License.*


