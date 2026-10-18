import hmac
import hashlib
import time
import sqlite3
import os
import json
import base64
import concurrent.futures

class UltimateZeroTrustMemoryEngine:
    def __init__(self, db_path="remenis_capbac_stress.db", master_secret=None):
        self.db_path = db_path
        self.master_secret = master_secret or os.environ.get("REMENIS_HMAC_KEY", "default-secure-sentinel-key-change-in-prod").encode('utf-8')
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zero_trust_ledger (
                sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                namespace TEXT NOT NULL,
                memory_id TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                prev_hash TEXT NOT NULL,
                signature TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _get_last_hash(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT signature FROM zero_trust_ledger ORDER BY sequence_id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        if not row:
            return hashlib.sha256(b"REMENIS_STRESS_GENESIS").hexdigest()
        return row[0]

    def _compute_hmac(self, data: str, secret=None) -> str:
        key = secret or self.master_secret
        return hmac.new(key, data.encode('utf-8'), hashlib.sha256).hexdigest()

    def issue_capability_token(self, holder_agent_id: str, target_namespace: str, permission: str, ttl_seconds: int = 300, custom_secret=None) -> str:
        expires_at = time.time() + ttl_seconds
        payload = {
            "holder": holder_agent_id,
            "namespace": target_namespace,
            "permission": permission,
            "expires": expires_at
        }
        payload_json = json.dumps(payload, sort_keys=True)
        token_sig = self._compute_hmac(payload_json, secret=custom_secret)
        
        token_data = {"payload": payload, "sig": token_sig}
        return base64.urlsafe_b64encode(json.dumps(token_data).encode('utf-8')).decode('utf-8')

    def verify_capability_token(self, token_str: str, required_namespace: str, required_permission: str) -> bool:
        try:
            decoded = json.loads(base64.urlsafe_b64decode(token_str.encode('utf-8')).decode('utf-8'))
            payload = decoded["payload"]
            provided_sig = decoded["sig"]

            payload_json = json.dumps(payload, sort_keys=True)
            expected_sig = self._compute_hmac(payload_json)
            if not hmac.compare_digest(expected_sig, provided_sig):
                return False

            if time.time() > payload["expires"]:
                return False

            if payload["namespace"] != required_namespace or payload["permission"] != required_permission:
                return False

            return True
        except Exception:
            return False

    def store_memory(self, namespace: str, memory_id: str, content: str):
        timestamp = time.time()
        prev_hash = self._get_last_hash()
        raw_data = f"{prev_hash}:{namespace}:{memory_id}:{content}:{timestamp}"
        signature = self._compute_hmac(raw_data)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO zero_trust_ledger (namespace, memory_id, content, timestamp, prev_hash, signature)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (namespace, memory_id, content, timestamp, prev_hash, signature))
        conn.commit()
        conn.close()

    def retrieve_memory(self, capability_token: str, namespace: str, memory_id: str, required_permission: str = "READ") -> str:
        if not self.verify_capability_token(capability_token, required_namespace=namespace, required_permission=required_permission):
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM zero_trust_ledger WHERE namespace = ? AND memory_id = ?', (namespace, memory_id))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

def run_stress_tests():
    db_file = "remenis_capbac_stress.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    engine = UltimateZeroTrustMemoryEngine(db_path=db_file)
    engine.store_memory("classified", "secret_key_99", "Nuclear launch authorization code: ALPHA-7")

    print("==================================================")
    print("🚀 STARTING ZERO-TRUST CAPBAC ADVERSARIAL STRESS TEST")
    print("==================================================\n")

    # --- STRESS TEST 1: The Time-Bomb Attack (Token Expiration) ---
    print("--- Stress Test 1: Token Expiration (TTL = 1 Second) ---")
    short_lived_token = engine.issue_capability_token("agent_temp", "classified", "READ", ttl_seconds=1)
    
    # Immediate access should succeed
    val_before = engine.retrieve_memory(short_lived_token, "classified", "secret_key_99")
    assert val_before == "Nuclear launch authorization code: ALPHA-7"
    print("[PASS] Token works immediately before TTL expiration.")

    print("[INFO] Sleeping for 2 seconds to let token expire...")
    time.sleep(2)

    # Delayed access should be rejected
    val_after = engine.retrieve_memory(short_lived_token, "classified", "secret_key_99")
    assert val_after is None
    print("[PASS] Perimeter successfully blocked expired capability token.\n")

    # --- STRESS TEST 2: In-Flight Payload Tampering Attack ---
    print("--- Stress Test 2: In-Flight Payload Tampering ---")
    legit_token = engine.issue_capability_token("logistics_bot", "logistics", "READ", ttl_seconds=60)
    
    # Adversary intercepts legit token, decodes base64, and tries to swap namespace to 'classified'
    decoded_bytes = base64.urlsafe_b64decode(legit_token.encode('utf-8'))
    token_obj = json.loads(decoded_bytes.decode('utf-8'))
    
    print(f"[ATTACKER] Intercepted payload, modifying namespace from '{token_obj['payload']['namespace']}' to 'classified'...")
    token_obj['payload']['namespace'] = "classified" # Tamper attempt without re-signing!
    
    tampered_bytes = json.dumps(token_obj).encode('utf-8')
    tampered_token = base64.urlsafe_b64encode(tampered_bytes).decode('utf-8')

    attack_result = engine.retrieve_memory(tampered_token, "classified", "secret_key_99")
    assert attack_result is None
    print("[PASS] Perimeter detected HMAC signature mismatch on tampered payload. Access denied!\n")

    # --- STRESS TEST 3: Permission Escalation Attack ---
    print("--- Stress Test 3: Permission Escalation (READ token used for WRITE) ---")
    read_only_token = engine.issue_capability_token("worker_agent", "classified", "READ", ttl_seconds=60)
    
    escalation_attempt = engine.retrieve_memory(read_only_token, "classified", "secret_key_99", required_permission="WRITE")
    assert escalation_attempt is None
    print("[PASS] Privilege escalation blocked: READ token denied WRITE-level permission scope.\n")

    # --- STRESS TEST 4: Rogue Master Key Forgery Attack ---
    print("--- Stress Test 4: Forged Token (Signed with Rogue Key) ---")
    rogue_secret = b"hacker-stolen-secret-key-123456"
    forged_token = engine.issue_capability_token("evil_bot", "classified", "READ", ttl_seconds=60, custom_secret=rogue_secret)
    
    forgery_result = engine.retrieve_memory(forged_token, "classified", "secret_key_99")
    assert forgery_result is None
    print("[PASS] Forged token rejected: Signature could not be verified against system master secret.\n")

    # --- STRESS TEST 5: High-Concurrency Authentication Flood ---
    print("--- Stress Test 5: High-Concurrency Flood (1,000 Concurrent Verifications) ---")
    flood_token = engine.issue_capability_token("speed_agent", "classified", "READ", ttl_seconds=60)
    
    def fire_request():
        return engine.retrieve_memory(flood_token, "classified", "secret_key_99")

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fire_request) for _ in range(1000)]
        results = [f.result() for f in futures]

    duration = time.time() - start_time
    successful_reads = sum(1 for r in results if r is not None)
    
    print(f"[METRICS] Handled 1,000 concurrent verifications in {duration:.4f} seconds.")
    assert successful_reads == 1000
    print(f"[PASS] 100% success rate under high-concurrency token flood.\n")

    print("==================================================")
    print("🔥 ALL 5 ADVERSARIAL CAPBAC STRESS TESTS PASSED")
    print("==================================================")

if __name__ == "__main__":
    run_stress_tests()
