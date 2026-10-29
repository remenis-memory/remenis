import hmac
import hashlib
import time
import sqlite3
import os
import json
import base64

class UltimateZeroTrustMemoryEngine:
    def __init__(self, db_path="remenis_zero_trust.db", master_secret=None):
        self.db_path = db_path
        self.master_secret = master_secret or os.environ.get("REMENIS_HMAC_KEY", "default-secure-sentinel-key-change-in-prod").encode('utf-8')
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Immutable memory ledger table
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
            return hashlib.sha256(b"REMENIS_ZERO_TRUST_GENESIS").hexdigest()
        return row[0]

    def _compute_hmac(self, data: str) -> str:
        return hmac.new(self.master_secret, data.encode('utf-8'), hashlib.sha256).hexdigest()

    def issue_capability_token(self, holder_agent_id: str, target_namespace: str, permission: str, ttl_seconds: int = 300) -> str:
        """
        Issues a cryptographically signed Capability Token (CCT) allowing a 
        specific non-human identity to access a target namespace.
        """
        expires_at = time.time() + ttl_seconds
        payload = {
            "holder": holder_agent_id,
            "namespace": target_namespace,
            "permission": permission,
            "expires": expires_at
        }
        payload_json = json.dumps(payload, sort_keys=True)
        token_sig = self._compute_hmac(payload_json)
        
        # Combine payload and signature into a secure bearer token string
        token_data = {"payload": payload, "sig": token_sig}
        return base64.urlsafe_b64encode(json.dumps(token_data).encode('utf-8')).decode('utf-8')

    def verify_capability_token(self, token_str: str, required_namespace: str, required_permission: str) -> bool:
        """Cryptographically verifies a capability token's authenticity, expiration, and scope."""
        try:
            decoded = json.loads(base64.urlsafe_b64decode(token_str.encode('utf-8')).decode('utf-8'))
            payload = decoded["payload"]
            provided_sig = decoded["sig"]

            # 1. Verify cryptographic signature
            payload_json = json.dumps(payload, sort_keys=True)
            expected_sig = self._compute_hmac(payload_json)
            if not hmac.compare_digest(expected_sig, provided_sig):
                print("[SECURITY ALERT] Invalid capability token signature!")
                return False

            # 2. Check Expiration
            if time.time() > payload["expires"]:
                print("[SECURITY ALERT] Capability token has expired!")
                return False

            # 3. Check Namespace & Permission Scope
            if payload["namespace"] != required_namespace or payload["permission"] != required_permission:
                print(f"[SECURITY ALERT] Token scope violation! Requested ({required_namespace}:{required_permission}), permitted ({payload['namespace']}:{payload['permission']}).")
                return False

            return True
        except Exception as e:
            print(f"[SECURITY ALERT] Malformed capability token: {e}")
            return False

    def store_memory(self, namespace: str, memory_id: str, content: str):
        """Appends memory to the immutable hash chain under a specific isolated namespace."""
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
        print(f"[STORED] Namespace '{namespace}' securely anchored memory '{memory_id}'.")

    def retrieve_memory(self, capability_token: str, namespace: str, memory_id: str) -> str:
        """Retrieves memory only if a valid, cryptographically verified capability token is presented."""
        # Enforce Zero-Trust CapBAC check before querying the database
        if not self.verify_capability_token(capability_token, required_namespace=namespace, required_permission="READ"):
            print("[ACCESS DENIED] Zero-Trust perimeter blocked unverified/unauthorized request.")
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content, timestamp, prev_hash, signature 
            FROM zero_trust_ledger 
            WHERE namespace = ? AND memory_id = ?
        ''', (namespace, memory_id))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        content, timestamp, prev_hash, stored_sig = row

        # Verify cryptographic ledger chain integrity (Step 1 Integration)
        raw_data = f"{prev_hash}:{namespace}:{memory_id}:{content}:{timestamp}"
        expected_sig = self._compute_hmac(raw_data)
        if not hmac.compare_digest(expected_sig, stored_sig):
            print(f"[CRITICAL TAMPERING ALERT] Ledger integrity compromised on memory '{memory_id}'!")
            return None

        print(f"[ZERO-TRUST ACCESS GRANTED] Valid cryptographic capability token verified for namespace '{namespace}'.")
        return content

if __name__ == "__main__":
    if os.path.exists("remenis_zero_trust.db"):
        os.remove("remenis_zero_trust.db")

    engine = UltimateZeroTrustMemoryEngine()

    # 1. Store confidential data in isolated enterprise namespaces
    engine.store_memory(namespace="finances", memory_id="txn_991", content="Q3 Revenue reserve verified at $4.2M.")
    engine.store_memory(namespace="logistics", memory_id="shipment_04", content="Customs clearance granted for cargo #4.")

    # 2. Issue a legitimate capability token for the logistics agent
    valid_token = engine.issue_capability_token(
        holder_agent_id="logistics_worker_01", 
        target_namespace="logistics", 
        permission="READ", 
        ttl_seconds=60
    )

    # 3. Legitimate Access (Token matches namespace and permission)
    print("\n--- Test 1: Legitimate Token-Authenticated Access ---")
    data = engine.retrieve_memory(capability_token=valid_token, namespace="logistics", memory_id="shipment_04")
    print(f"Retrieved Content: {data}")

    # 4. Unauthorized Cross-Namespace Espionage (Logistics agent tries to use its token to read finances)
    print("\n--- Test 2: Cross-Namespace Capability Hijacking Attack ---")
    engine.retrieve_memory(capability_token=valid_token, namespace="finances", memory_id="txn_991")

    # 5. Tampered/Fake Token Attack
    print("\n--- Test 3: Forged Capability Token Attack ---")
    engine.retrieve_memory(capability_token="eyJob2xkZXIiOiBoYWNrZXIiLCJuYW1lc3BhY2UiOiAiZmluYW5jZXMiLCJwZXJtaXNzaW9uIjogIlJFQ0QiLC", namespace="finances", memory_id="txn_991")
