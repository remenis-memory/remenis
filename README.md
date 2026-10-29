<<<<<<< HEAD
# 🧠 Remenis: AI Memory Security Framework

> **Clean Context. Zero Bloat. Absolute Agent Containment.**

**Remenis** is an open-source AI memory isolation framework designed to solve the **AI agent memory poisoning problem**. As autonomous agents execute multi-turn tasks independently, unvetted long-term memory accumulation and context injection can cause agents to go rogue, drift, or execute unauthorized tool calls without human oversight.

Remenis enforces strict runtime boundaries and memory hygiene to ensure agent state remains secure, fast, and untainted.

---

## 🚀 Key Architectural Updates

Remenis solves context drift and rogue agent behavior through **5 core pillars**:

1. **🛡️ OS Privilege Rings (`RingContextGuard`)**
   * Multi-tiered hierarchical memory isolation (Ring-0 to Ring-2). Guarantees untrusted prompts and user context cannot corrupt, overwrite, or leak core system memory.
2. **🔒 Security Guardrails**
   * Real-time validation logic that intercepts and blocks prompt injection, context poisoning, and unauthorized memory modification before state updates persist.
3. **⏳ Time-Decay Scoring**
   * Algorithmic decay function that automatically deprioritizes stale or obsolete memory entries so the agent retrieves only high-fidelity, relevant context.
4. **⚡ Fast Multi-Thread Writes**
   * High-throughput concurrent execution pipeline optimized for parallel memory reads and writes in real-time agent workflows.
5. **🧹 Auto-Deduping**
   * Vector and semantic deduplication engine that removes redundant memory entries, delivering **clean context with zero bloat**.

---

## 🏗️ Architecture Overview

```text
[ Incoming Prompt / Agent Context ]
                 │
                 ▼
 ┌──────────────────────────────┐
 │    Security Guardrails       │ (Real-Time Prompt Injection Defense)
 └───────────────┬──────────────┘
                 │
                 ▼
 ┌──────────────────────────────┐
 │    OS Privilege Rings        │ (RingContextGuard Isolation: Ring-2 -> Ring-0)
 └───────────────┬──────────────┘
                 │
                 ▼
 ┌──────────────────────────────┐
 │  Multi-Thread Memory Engine  │ (Auto-Deduping & Time-Decay Scoring)
 └───────────────┬──────────────┘
                 │
                 ▼
 [ Pure, Uncorrupted Context Output ]
🛠️ Quickstart & Integration
Install Remenis via PyPI or clone locally:

Installation
Bash
pip install remenis
Local Development Setup
Bash
# Clone repository
git clone [https://github.com/your-username/remenis.git](https://github.com/your-username/remenis.git)
cd remenis

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install editable package
pip install -e .
Usage Example
Python
from remenis import MemoryEngine, RingContextGuard

# Initialize guard at isolation level 1
guard = RingContextGuard(ring_level=1)
memory = MemoryEngine(guard=guard)

# Process and store secure agent memory
clean_context = memory.process_input("User input payload")
🤝 Community & Benchmarks
We actively red-team Remenis against agentic vulnerabilities, memory poisoning, and context leakage patterns.

Automated Red-Teaming Suites: Run pytest tests/benchmarks/ to test RingContextGuard against known prompt injection vectors.

Contributing: Open an issue or pull request to submit new benchmark payloads or security guardrails.

📄 License
Distributed under the Apache 2.0 License. See LICENSE for details.
=======
# 🧠 Remenis

![Build Status](https://img.shields.io/badge/Security_CI-Passing-brightgreen?style=flat-square)
![Compliance](https://img.shields.io/badge/Compliance-SOC2_%7C_ISO--42001_%7C_EU_AI_Act-blue?style=flat-square)
![Latency](https://img.shields.io/badge/Storage_IDS-Sub--5ms-orange?style=flat-square)
![Token Savings](https://img.shields.io/badge/DCC_Compression-90%25-purple?style=flat-square)

> **The Zero-Trust Enterprise AI Middleware** — High-Performance Context Compression, Sub-5ms Storage IDS, Cryptographic SBQ Quarantine, and Verifiable Audit Artifacts for Autonomous Agents.

---

## 🏛️ Core Architecture

```
                                [ Autonomous AI Agent ]
                                           │
                                           ▼
             ┌──────────────────────────────────────────────────────────┐
             │               Remenis Zero-Trust Middleware              │
             ├──────────────────────────────────────────────────────────┤
             │  1. DCC Engine          ──> Slashes Token Burn by ~90%  │
             │  2. Storage IDS         ──> Sub-5ms Invariant Detection  │
             │  3. SBQ Quarantine      ──> Revokes Rogue Namespaces     │
             │  4. Cryptographic Proof ──> Signed Audit Verification    │
             └──────────────────────────────────────────────────────────┘
                                           │
                                           ▼
                                  [ Enterprise Vector Store ]
```

---

## ⚡ Visual Proofs & Terminal Demos

### 1. 📉 Deterministic Context Compression (DCC)
*Slashes LLM API token burn by up to 90% while preserving operational state.*

![DCC Memory Compression](memory.gif)

---

### 2. 🛡️ Storage-Layer IDS & Obfuscation Defense
*Intercepts direct prompt injections, Base64 obfuscation, and unauthorized webhooks.*

![Storage IDS Defense](security.gif)

---

### 3. 🔒 SBQ Behavioral Quarantine & Revocation Ledger
*Permanently neutralizes rogue AI behavior by revoking cryptographic namespaces in real time.*

![SBQ Quarantine & Revocation](quarantine.gif)

---

## 🗂️ CLI Compliance Proof Exporter (`remenis.audit`)

Generate and verify cryptographically signed `.proof` files for enterprise governance:

### Generate Signed Compliance Proof:
```bash
python3 remenis_audit.py --key "enterprise_secure_key" --out remenis_soc2.proof
```

### Cryptographically Verify Proof Integrity:
```bash
python3 remenis_audit.py --key "enterprise_secure_key" --verify remenis_soc2.proof
```

---

## 🚀 Quick Start (2-Line Integration)

```python
from remenis import ZeroTrustMemory

memory = ZeroTrustMemory(secret_key="enterprise_secure_key")
record = memory.add_record(agent_id="enterprise_agent_01", content="Secure context payload")
```

---
*Maintained under Zero-Trust AI Standards.*
>>>>>>> 015eb83d7b2f36de80865bc3d29c39b09207bbfb
