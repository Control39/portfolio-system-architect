# Human-AI Workflow: My Leadership Process
*Visual proof of Lead Architect role. Not 'AI copies prompts' — orchestrated symphony. Addresses skeptic #3: 'Human is the author'.*

## Workflow Diagram
```mermaid
graph TD
    A[1. I set Goal<br/>+ Constraints<br/>(e.g. local-first, no vendor-lock)] --> B[2. AI Generates<br/>3-5 Variants]
    B --> C{3. I Evaluate<br/>Trade-offs}
    C -->|Accept| D[4a. Integrate<br/>w/ Ecosystem]
    C -->|Reject<br/>+Reason| E[4b. Clarify Prompt<br/>w/ Feedback]
    E --> B
    D --> F[5. I Document<br/>Decision + Why]
    F --> G[Live System<br/>+Evidence Loop]
    style A fill:#e1f5fe
    style C fill:#fff3e0
    style F fill:#e8f5e8
```

## Cycle Explanation
1. **Goal-Setting (Human)**: Define problem, non-negotiables (e.g., 'offline RAG for 10k notes').
2. **Generation (AI)**: Produce options.
3. **Critical Eval (Human)**: Check feasibility, trade-offs (e.g., speed vs cost).
4. **Iterate/Reject (Human)**: 60% proposals rejected (see human-decisions.md).
5. **Document (Human)**: Log why chosen (ADR-style).
6. **Evidence Loop**: Metrics validate (impact.md).

## Real Example: IT-Compass RAG
- Goal: Local vector DB.
- AI: FAISS + Pinecone.
- My Eval: FAISS slow CPU; Pinecone SaaS-lock.
- Reject → ChromaDB (persistent, Docker).
- Result: 111+ evidence queries in 150ms.

*This process: From chaos → ecosystem. Replicable via noobs-guide.md. My 3-year evolution proves it works for noobs.*

*Updated: 2026-XX.*

