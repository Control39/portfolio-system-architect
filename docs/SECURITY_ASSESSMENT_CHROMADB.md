# Security Assessment: ChromaDB CVE-2026-45829

## Vulnerability Details

- **CVE ID:** CVE-2026-45829
- **Package:** chromadb
- **Version:** 1.5.9
- **Type:** Pre-authentication code injection
- **Severity:** Critical
- **Affected Endpoint:** `/api/v2/tenants/{tenant}/databases/{db}/collections`

## Vulnerability Description

A pre-authentication, code injection vulnerability in version 1.0.0 or later of the ChromaDB Python project allows an unauthenticated attacker to run arbitrary code on the server by sending a malicious model repository and `trust_remote_code` set to `true` in the `/api/v2/tenants/{tenant}/databases/{db}/collections` endpoint.

## Project Usage Assessment

### Current Implementation

The project uses ChromaDB **exclusively in local/persistent mode**:

```python
self.client = chromadb.PersistentClient(
    path=str(self.persist_directory),
    settings=Settings(anonymized_telemetry=False),
)
```

### Why This CVE Does NOT Apply

1. **No Server Deployment**: The project does not run ChromaDB server
2. **No HTTP Endpoint Access**: Local `PersistentClient` does not expose HTTP API
3. **No trust_remote_code Usage**: The vulnerable `trust_remote_code=True` parameter is never used
4. **No Multi-tenant API**: The `/api/v2/tenants/...` endpoint path is not accessible

### Files Using ChromaDB

- `src/vector_store/chroma_impl.py` - Local vector storage implementation
- `src/vector_store/config.py` - Configuration for local storage
- `apps/embedding_agent/chroma_indexer.py` - Local document indexing
- `apps/embedding_agent/embedder.py` - Local embeddings
- `apps/mcp_server/src/tools/chroma_tools.py` - Local tool integration

## Mitigation Status

✅ **No action required** - The vulnerability is not exploitable in current configuration.

## Recommendations

1. Continue using ChromaDB in local mode only
2. Do NOT deploy ChromaDB server with exposed HTTP API
3. Do NOT use `trust_remote_code=True` parameter
4. Monitor ChromaDB releases for official patch (if server deployment is planned)

## References

- [ChromaDB GitHub](https://github.com/chroma-core/chroma)
- [CVE Details](https://nvd.nist.gov/vuln/detail/CVE-2026-45829)

---

**Assessment Date:** 2026-06-24
**Assessed By:** AI Security Assistant
**Status:** ✅ Not Affected - Local Mode Only
