# 🧠 Remenis

A lightweight, high-performance local memory layer for AI agents. Remenis cuts token consumption by 60–70% using vector-based storage (`sqlite-vec`), while protecting your agent pipelines from prompt injection, memory drift, and context pollution.

## What it solves
AI agents love to drown in their own context windows—burning tokens, forgetting old tasks, or getting derailed by injected prompts. Remenis gives your agents a structured, self-healing memory vault backed by SQLite.

## Core Features
1. **Vector Storage & Dedup** — Slashes token usage by 60-70% using `sqlite-vec`.
2. **Real-Time Poison Guards** — Intercepts prompt injections before they contaminate storage.
3. **Immutable Provenance Hashing** — SHA-256 integrity binding for task intents.
4. **Self-Healing Rollbacks** — Instant temporal snapshots to recover from corrupted agent turns.
5. **Time-Decay Entropy** — Exponentially fades stale memories to keep active contexts lean.
