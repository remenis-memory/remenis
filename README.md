# Remenis Memory

High-performance, local-first AI memory infrastructure powered by SQLite-Vec, local compression, and guardrails. Designed for developers who need robust, zero-trust context management for autonomous agents.

---

## 🚀 Quick Start

```bash
pip install remenis-memory
Python
from remenis import RemenisCore

engine = RemenisCore(db_path="remenis.db")
engine.store(key="agent:task_1", value="Context compressed and secured locally.")
🔌 Framework Ecosystem
Remenis provides native adapters for your favorite orchestration frameworks:

CrewAI (Agent memory storage & security filtering)

AutoGen (Multi-agent context management)

LangChain (Drop-in vectorstore/retriever middleware)

LlamaIndex (Vector index wrapper for token-optimized retrieval)

Semantic Kernel (Enterprise agent memory plugin)

🔒 Remenis Enterprise & Compliance Tier (Coming Soon)
Note: The advanced security features, quarantine protocols, and compliance ledgers shown below are part of the Remenis Enterprise closed-source tier, which is currently in development and coming soon for enterprise deployments.

🛡️ License
Distributed under the MIT License. See LICENSE for more information.
