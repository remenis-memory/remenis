# 🧠 Remenis

![Build Status](https://img.shields.io/badge/Security_CI-Passing-brightgreen?style=flat-square)
![Compliance](https://img.shields.io/badge/Compliance-SOC2_%7C_ISO--42001_%7C_EU_AI_Act-blue?style=flat-square)
![Latency](https://img.shields.io/badge/Storage_IDS-Sub--5ms-orange?style=flat-square)
![Token Savings](https://img.shields.io/badge/DCC_Compression-90%25-purple?style=flat-square)

> **The Zero-Trust Enterprise AI Middleware** — High-Performance Context Compression, Sub-5ms Storage IDS, Cryptographic SBQ Quarantine, and Verifiable Audit Artifacts for Autonomous Agents.

---

## 🏛️ Core Architecture
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
Cryptographically Verify Proof Integrity:
Bash
python3 remenis_audit.py --key "enterprise_secure_key" --verify remenis_soc2.proof
🚀 Quick Start (2-Line Integration)
Install the package via PyPI:

Bash
pip install remenis-memory
Python
from remenis import ZeroTrustMemory

memory = ZeroTrustMemory(secret_key="enterprise_secure_key")
record = memory.add_record(agent_id="enterprise_agent_01", content="Secure context payload")
Maintained under Zero-Trust AI Standards.
