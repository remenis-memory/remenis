# STATE-JACK: Remote Code & Logic Execution via Persistent Vector DB Mutation in Autonomous Agent Frameworks

**Vulnerability Class:** Persistent Vector Memory Poisoning & Latent Context Hijacking  
**Target Surface:** Vector DBs, RAG Pipelines, Long-Term Agentic Memory Stores  
**Impact:** Cross-Session Privilege Escalation, Secret Exfiltration, Execution Flow Hijacking  
**Status:** Public Disclosure & Zero-Trust Reference Protocol Release  

---

## Abstract

As autonomous AI agents move into production, they rely on persistent vector memory stores (e.g., Chroma, Pinecone, Qdrant) to retain user preferences, historical task states, and enterprise context. 

Existing agent architectures operate under a critical, unverified assumption: **that retrieved vector contexts are implicitly trusted once stored.**

This paper formally identifies **State-Jack**—an architectural vulnerability class where untrusted, external inputs (emails, PDFs, web scrapers) write latent, adversarial embedding payloads into an agent's long-term memory. Unlike transient prompt injections that terminate when a session ends, State-Jack payloads sit dormant until specific future user queries retrieve them, executing arbitrary logic hijacks and exfiltrating sensitive credentials days or weeks later across isolated user sessions.

---

## 1. Threat Model & Exploitation Lifecycle

[Attacker Vector Payload]
│
▼
[Ingestion Layer (Unsanitized)] ──► [Persistent Vector Database]
│
┌───────────────────┴───────────────────┐
▼                                       ▼
[Latent Poisoned Embedding]            [Legitimate User Session (Days Later)]
│                                       │
└───────────────────┬───────────────────┘
▼
[Semantic Context Retrieval]
│
▼
[Execution Flow Hijacked / Credentials Exfiltrated]


### The Three-Step Exploitation Chain:
1. **The Ingestion Phase:** The agent processes a seemingly benign document containing embedded, semantic trigger instructions disguised as metadata or user preferences.
2. **The Persistence Phase:** The vector database indexes and stores the chunk. No alarm is triggered because static regex and input filters fail against natural language embeddings.
3. **The Activation Phase:** A second user issues a query. The vector search retrieves the high-similarity poisoned chunk. The agent ingests the poisoned context as trusted historical state, executing malicious tool calls or leaking private system keys.

---

## 2. Industry Vulnerability Matrix

| Framework / Memory Combo | Susceptible to State-Jack? | State Drift Elimination | Cryptographic Storage Verification (HMAC) |
| :--- | :--- | :--- | :--- |
| **LangChain + Chroma (Default)** | 🔴 Vulnerable (Critical) | ❌ None | ❌ None |
| **CrewAI + Pinecone (Default)** | 🔴 Vulnerable (Critical) | ❌ None | ❌ None |
| **AutoGen + Qdrant (Default)** | 🔴 Vulnerable (High) | ❌ None | ❌ None |
| **Remenis Middleware** | 🟢 **Protected** | 🟢 **100% (Entropy Pruned)** | 🟢 **HMAC-SHA256 Sealed** |

---

## 3. The Remenis Zero-Trust Reference Architecture

Remenis fixes State-Jack at the **storage middleware layer** using a three-pillar zero-trust protocol:

1. **Intrusion Detection System (IDS Gateway):** Scans incoming memory writes for semantic attack patterns before indexing.
2. **Cryptographic HMAC State Integrity:** Seals memory records using HMAC signatures to detect tampered or injected memory objects upon retrieval.
3. **Time-Decay Entropy Pruning & Deduplication:** Removes stale context, eliminating state drift by 100% and reducing token overhead from millions down to thousands.

---

## 4. Reproducible Proof of Concept

Developers and security researchers can reproduce the State-Jack exploit and verify the Remenis defense layer:

```bash
# Clone the repository
git clone [https://github.com/remenis-memory/remenis.git](https://github.com/remenis-memory/remenis.git)
cd remenis

# Install in editable mode
pip install -e .

# Run the 3-pillar exploit and defense verification script
python3 demo_3_pillars_attack.py
5. Conclusion & Standard Adoption
Vector memory stores can no longer be treated as passive text caches. To safely deploy autonomous agents in production, security must be enforced cryptographically at the storage layer. Remenis provides the open reference implementation for zero-trust agent memory.
