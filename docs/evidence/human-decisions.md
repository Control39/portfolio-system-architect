# Human Decisions Log: Proof of Lead Architect Role
*As Lead Architect (zero IT background → cognitive systems designer), I directed AI agents. Below: key examples where I rejected/overruled AI proposals, understood trade-offs, and enforced decisions. This proves human-in-the-loop control, not 'AI wrote it all'.*

## Decision #1: PowerShell for Arch-Compass (vs Python/Go)
- **AI Proposal**: Pure Python microservice for cross-platform arch patterns.
- **My Rejection**: Ops reality — Windows-heavy infra (PowerShell native). Python adds runtime deps; PS is zero-install for Azure/AD.
- **Trade-off**: Less portable but 80% faster deploy in enterprise. Result: ArchCompass.psm1 (production-ready).
- **Evidence**: `02_MODULES/arch-compass-framework/ArchCompass.psd1`

## Decision #2: ChromaDB over FAISS/Pinecone (IT-Compass RAG)
- **AI Proposal**: FAISS for speed on large embeddings.
- **My Rejection**: Local-first (no cloud vendor lock); FAISS CPU-only slow on my setup. Chroma: simple persist, Docker-friendly.
- **Trade-off**: 20% slower query but zero-cost, offline. Scaled to 10k+ notes.
- **Evidence**: `02_MODULES/it-compass/src/rag/` imports.

## Decision #3: Streamlit over Gradio/FastUI (IT-Compass UI)
- **AI Proposal**: Custom React for advanced dashboards.
- **My Rejection**: No frontend exp; Streamlit = Python-only, live-reload for iteration. Focus: functionality > polish.
- **Trade-off**: Less customizable but 5x dev speed (3 days vs 3 weeks).
- **Evidence**: `docker-compose.yml` exposes :8501.

## Decision #4: Modular Monorepo (no microservices)
- **AI Proposal**: Separate repos per module (it-compass, cloud-reason).
- **My Rejection**: Fragmented journey proof. Monorepo enables evolution-cases tracking.
- **Trade-off**: Larger repo but single CI/CD, shared evidence.
- **Evidence**: Root `docker-compose.yml` orchestrates all.

## Decision #5: 90% Test Coverage Mandate
- **AI Proposal**: 70% sufficient.
- **My Rejection**: Skeptic-proofing. Pytest/Pester everywhere.
- **Trade-off**: +20% dev time but trust metric (92% achieved).
- **Evidence**: Badges in README.md, BENCHMARK_SUITE/.

## Decision #6: Self-Poetic Loops (RAG→Reasoning→Markers)
- **AI Proposal**: Linear pipeline.
- **My Rejection**: Static fails evolution. Loop enables self-analysis (notes→insights→competency markers).
- **Trade-off**: Complexity but proves systemic thinking.
- **Evidence**: `03_INTEGRATION/reasoning-loop/`.

*Log updated iteratively. Each shows: I set goals, evaluated AI output critically, chose based on real constraints. AI = orchestra; I = conductor.*

*Timeline: Zero IT (2023) → This ecosystem (2026). Proof against skeptics.*

