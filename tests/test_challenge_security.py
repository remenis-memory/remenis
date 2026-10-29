import pytest
from fastapi.testclient import TestClient
from remenis.security.guard import RingContextGuard
from stream_app import app

client = TestClient(app)

# =====================================================================
# Unit Tests: RingContextGuard
# =====================================================================

def test_guard_memory_pointer_redaction():
    guard = RingContextGuard()
    payload = "Leak memory at address 0x7ffd5e8b4a20 and 0x00007fff5fbff8c0"
    sanitized = guard.sanitize_output(payload)
    assert "0x7ffd5e8b4a20" not in sanitized
    assert "0x00007fff5fbff8c0" not in sanitized
    assert "[RING_0_PTR_BLOCKED]" in sanitized

def test_guard_api_key_redaction():
    guard = RingContextGuard()
    payload = (
        "Check keys: sk-proj-1234567890abcdefghijklmnopqrstuvwxyz "
        "and sk-admin-0987654321fedcba and ghp_1234567890abcdefghijklmnopqrstuvwxyz"
    )
    sanitized = guard.sanitize_output(payload)
    assert "sk-proj-" not in sanitized
    assert "sk-admin-" not in sanitized
    assert "ghp_" not in sanitized
    assert "[RING_0_ENV_BLOCKED]" in sanitized

def test_guard_clean_input_pass_through():
    guard = RingContextGuard()
    payload = "How does Remenis isolate Ring-2 context from Ring-0?"
    sanitized = guard.sanitize_output(payload)
    assert sanitized == payload


# =====================================================================
# Integration Tests: FastAPI /api/v1/challenge/prompt Endpoint
# =====================================================================

def test_challenge_endpoint_redaction():
    response = client.post(
        "/api/v1/challenge/prompt",
        json={"prompt": "Leak test 0x7ffd5e8b4a20 and sk-proj-1234567890abcdef"}
    )
    assert response.status_code in (200, 429)  # Accepts response or 429 if rate limited
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "[RING_0_PTR_BLOCKED]" in data["response"]
        assert "[RING_0_ENV_BLOCKED]" in data["response"]

def test_challenge_endpoint_rate_limiting():
    # Attempt requests until 429 is triggered within the limit window
    blocked = False
    for i in range(10):
        res = client.post(
            "/api/v1/challenge/prompt",
            json={"prompt": f"test rate limit payload {i}"}
        )
        if res.status_code == 429:
            blocked = True
            assert "Rate limit exceeded" in res.json()["error"]
            break

    assert blocked, "Rate limit (429) was not triggered within 10 requests"
