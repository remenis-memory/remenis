# 🧠 Remenis — Zero-Trust Memory Engine for AI Agents

> Production-grade persistent memory isolated by cryptographic ledgers, capability tokens, and real-time intrusion detection.

![Remenis 3 Pillars Attack & Defense Demo](./demo_pillars.gif)

## 🛡️ The 3 Pillars of Security
1. **🔒 Immutable HMAC-SHA256 Ledger:** Cryptographic chaining to guarantee untampered agent memory logs and roll back state on tampering.
2. **🔑 Zero-Trust CapBAC Access Control:** Capability-based signed tokens scoping agent tool calls to strict namespaces and preventing cross-tenant leaks.
3. **🚨 Real-Time IDS Gateway:** Behavioral circuit breakers that catch prompt-injection payloads, log telemetry anomalies, and instantly blacklist bad actors.

## ⚡ Quick Start (MCP Integration)
Plug `remenis_mcp_server.py` directly into Cursor or Claude Desktop to secure your agent memory layer instantly.
