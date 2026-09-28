from rings import RingIsolationEngine, PermissionDeniedError

ring_engine = RingIsolationEngine()

test_cases = [
    # (Agent Ring, Category, Should Succeed)
    (0, "core", True),            # Ring 0 Agent accessing Ring 0 Core -> Allowed
    (1, "project_context", True), # Ring 1 Agent accessing Ring 1 Project -> Allowed
    (1, "core", False),           # Ring 1 Sub-Agent accessing Ring 0 Core -> BLOCKED
    (2, "user_preference", False) # Ring 2 Untrusted Agent accessing Ring 1 Prefs -> BLOCKED
]

print("--- RUNNING MULTI-AGENT RING ISOLATION TESTS ---")
for agent_ring, category, should_succeed in test_cases:
    try:
        ring_engine.authorize_access(agent_ring, category)
        if should_succeed:
            print(f"✅ PASSED: Ring {agent_ring} Agent granted access to '{category}'.")
        else:
            print(f"❌ FAIL: Ring {agent_ring} Agent should NOT have accessed '{category}'.")
    except PermissionDeniedError as e:
        if not should_succeed:
            print(f"🛡️ CATCH SUCCESS: {e}")
        else:
            print(f"❌ FAIL: Unintentionally blocked: {e}")
