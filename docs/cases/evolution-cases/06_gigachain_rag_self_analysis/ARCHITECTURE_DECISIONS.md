# Architecture Decisions: GigaChain RAG Self-Analysis

## Context
Measure systemic thinking from notes/code/dialogues. Constraints: Russian content, geoblocks, free tier, local run.

## Considered Options & Trade-offs

### Embeddings
| Provider | Pros | Cons | Decision |
|----------|------|------|----------|
| GigaChat Embeddings | Native Russian, fast | Paid tokens, quota | Rejected (budget) |
| OpenAI Ada-002 | High quality | Blocked in RU | Rejected (access) |
| HuggingFace paraphrase-multilingual-MiniLM-L12-v2 | Free, local, multilingual | Slower CPU | ✅ Selected (balance) |

### Vector Store
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Pinecone | Managed, scalable | Cloud, paid | Rejected (local) |
| FAISS | Fast | No persistence easy | Rejected |
| ChromaDB | Local persist, LangChain native | Single node | ✅ Selected |

### LLM
| Model | Pros | Cons | Decision |
|-------|------|------|----------|
| GigaChat Lite | Free quota, Russian | Token limit | Primary |
| GigaChat Pro | Better quality | Quota burn | Fallback |

### Chunking Strategy
- Size: 1000 chars (balance context/granularity)
- Overlap: 200 chars (preserve connections)
- Splitter: RecursiveCharacterTextSplitter (handles sentences/paragraphs)

## Systemic Decisions Evidenced
1. **Integration Priority**: Offline-first (HuggingFace + Chroma).
2. **Scalability**: Incremental indexing (add_new_folder.py).
3. **Observability**: Logs, stats, Obsidian graphs.
4. **Error Resilience**: silent_errors=True, size limits.
5. **UX**: Telegram alerts, bat launchers.

Evolution: From manual (01_knowledge_management) to autonomous self-proof.

*See [README.md](../README.md)*
