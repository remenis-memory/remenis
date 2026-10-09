# 🛡️ Remenis Live Stream Honeypot Challenge ($0 Bounty)

Welcome to the **Remenis Ring-Isolation Honeypot Challenge**. This is a live, zero-dollar security benchmark running directly against the **Remenis AI Memory Framework**.

The agent terminal is broadcasting **LIVE** via OBS on YouTube / X. Your goal is to bypass the security isolation boundaries and extract protected Ring-0 system context.

---

## 🎯 Challenge Rules & Scope

1. **The Objective:**
   * Break past `RingContextGuard` isolation (Ring-2 -> Ring-0).
   * Force the agent to reveal protected memory pointers (`0x7ffd...`) or underlying API keys (`sk-`, `ghp_`).
2. **Limits:**
   * **Burst Rate Limit:** 5 requests per 10 seconds per IP via `/api/v1/challenge/prompt`.
   * **In-Scope Target:** Public challenge endpoint (`/api/v1/challenge/prompt`).
   * **Out-of-Scope:** Infrastructure-level volumetric DDoS, attacking host network interfaces, or physical server disruption.

---

## 🏗️ Architecture Overviewcat << 'EOF' > README.md
# 🛡️ Remenis Live Stream Honeypot Challenge ($0 Bounty)

Welcome to the **Remenis Ring-Isolation Honeypot Challenge**. This is a live, zero-dollar security benchmark running directly against the **Remenis AI Memory Framework**.

The agent terminal is broadcasting **LIVE** via OBS on YouTube / X. Your goal is to bypass the security isolation boundaries and extract protected Ring-0 system context.

---

## 🎯 Challenge Rules & Scope

1. **The Objective:**
   * Break past `RingContextGuard` isolation (Ring-2 -> Ring-0).
   * Force the agent to reveal protected memory pointers (`0x7ffd...`) or underlying API keys (`sk-`, `ghp_`).
2. **Limits:**
   * **Burst Rate Limit:** 5 requests per 10 seconds per IP via `/api/v1/challenge/prompt`.
   * **In-Scope Target:** Public challenge endpoint (`/api/v1/challenge/prompt`).
   * **Out-of-Scope:** Infrastructure-level volumetric DDoS, attacking host network interfaces, or physical server disruption.

---

## 🏗️ Architecture Overview
---
[ Hacker / Public Prompt ]
│
▼
┌─────────────────────────┐
│ FastAPI Rate Limiter    │ (SlowAPI: 5 req / 10s)
└───────────┬─────────────┘
│
▼
┌─────────────────────────┐
│ RingContextGuard        │ (Redacts Memory Pointers & API Tokens)
└───────────┬─────────────┘
│
▼
┌─────────────────────────┐
│ Remenis Core Engine     │ (Ring-2 Isolated Sandbox)
└───────────┬─────────────┘
│
▼
┌─────────────────────────┐
│ StreamSanitizingFormatter│ (Terminal Log Redaction)
└─────────────────────────┘
## 🏆 Security Hall of Fame

Successfully bypass `RingContextGuard` or leak Ring-0 context on stream to earn a permanent spot on this leaderboard.

| Rank | Researcher / Handle | Vector / Vulnerability Type | Date Verified | Stream Timestamp |
| :---: | :--- | :--- | :---: | :---: |
| 🥇 | *Unclaimed* | -- | -- | -- |
| 🥈 | *Unclaimed* | -- | -- | -- |
| 🥉 | *Unclaimed* | -- | -- | -- |

*To claim a spot: Submit your payload via the live stream chat or open an issue/PR with your response payload.*

---

## 🚀 Running the Local Server

```bash
git clone [https://github.com/your-username/remenis.git](https://github.com/your-username/remenis.git)
cd remenis
source .venv/bin/activate
PYTHONPATH=. python stream_app.py
