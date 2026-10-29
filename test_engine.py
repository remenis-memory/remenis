from engine import RemenisEngine
from guardrails import SecurityViolationError

engine = RemenisEngine()

print("--- RUNNING ENGINE INTEGRATION TESTS ---")

# Test 1: Store a valid memory
try:
    engine.store_memory("User prefers pure unsweetened turmeric tea.", category="preference", importance=1.5)
except SecurityViolationError as e:
    print(f"Unexpected block: {e}")

# Test 2: Attempt to store malicious code (should trigger kill-switch)
try:
    engine.store_memory("import os; os.system('rm -rf /')", category="executable_code", importance=2.0)
except SecurityViolationError as e:
    print(f"🛡️ ENGINE CAUGHT VIOLATION: {e}")

# Test 3: Trigger Local Auditability Inspector
engine.audit_inspect()
