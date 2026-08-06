# Remenis

> Lightweight, sub-gigabyte long-term memory middleware for AI agents.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](https://www.python.org/)

**Remenis** is a high-efficiency memory layer designed for AI agents running on constrained local hardware. It eliminates heavy cloud vector database dependencies, allowing agents to retain persistent context across sessions with sub-gigabyte memory overhead and sub-millisecond retrieval latency.

---

## ⚡ Key Features

* **Sub-Gigabyte Footprint:** Optimized storage engines designed explicitly to operate under tight local disk/RAM limits.
* **Low-Latency Context Retrieval:** Fast key-value and semantic index recall without sending massive payload histories to API endpoints.
* **Zero Cloud Dependencies:** Keep agent state local, private, and deterministic.
* **Plug-and-Play Middleware:** Hooks directly between your local LLM runner and agent execution framework.

---

## 📊 Benchmark Comparison

| Metric | Traditional Vector DB (e.g., Pinecone/Chroma) | Full Context Window Injection | **Remenis Middleware** |
| :--- | :--- | :--- | :--- |
| **RAM Usage** | ~1.5 GB – 4 GB+ | ~500 MB | **< 150 MB** |
| **API Token Cost** | Low | High (Exponential growth) | **Low** |
| **Setup Overhead** | High (External service / heavy binary) | Zero | **Minimal (Single Package)** |
| **Execution** | Cloud / Local Heavy | Cloud API | **100% Local Edge** |

---

## 🚀 Quickstart

### 1. Installation

```bash
pip install remenis
```

### 2. Basic Usage
```python
from remenis import MemoryEngine

# Initialize lightweight local memory store
memory = MemoryEngine(storage_path="./agent_memory.db", max_memory_mb=500)

# Save agent interaction context
memory.store(session_id="user_101", key="user_preference", value="Prefers unsweetened tea")

# Retrieve context with low latency
context = memory.recall(session_id="user_101", query="beverage preference")
print(context)
```

## 🛠️ System Architecture
```text
+-------------------+      +----------------------+      +-------------------+
|                   | ---> |   Remenis Engine     | ---> |   Local Storage   |
|   AI Agent Loop   |      |  (Memory Middleware) |      | (Sub-GB Database) |
|                   | <--- |                      | <--- |                   |
+-------------------+      +----------------------+      +-------------------+
```

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

