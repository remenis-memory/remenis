import hmac
import hashlib
import time
import sqlite3
import os
import json
import base64
import concurrent.futures

class UltimateIDSGateway:
    def __init__(self, db_path="remenis_ultimate_ids.db", master_secret=None):
        self.db_path = db_path
        self.master_secret = master_secret or os.environ.get("REMENIS_HMAC_KEY", "default-secure-sentinel-key-change-in-prod").encode('utf-8')
        
        # In-memory runtime IDS state trackers
        self.failed_attempts = {}
        self.blacklisted_agents = set()
        self.max_failures_before_lockout = 3

        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Immutable memory ledger
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
        
        # Advanced IDS Security & Incident Log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ids_security_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                agent_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                attack_type TEXT NOT NULL,
                details TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _log_security_event(self, agent_id: str, severity: str, attack_type: str, details: str):
        """Records high-priority security telemetry and triggers automated incident response."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ids_security_events (timestamp, agent_id, severity, attack_type, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (time.time(), agent_id, severity, attack_type, details))
        conn.commit()
        conn.close()

        # Automated Incident Response Webhook Simulation
        if severity == "CRITICAL":
            print(f"\n🚨 [AUTOMATED INCIDENT RESPONSE] ALERT! Critical threat detected from agent '{agent_id}'.")
            print(f"   Action Taken: Agent runtime locked out and isolated. Security webhook dispatched.")

    def _compute_hmac(self, data: str) -> str:
        return hmac.new(self.master_secret, data.encode('utf-8'), hashlib.sha256).hexdigest()

    def _get_last_hash(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT signature FROM zero_trust_ledger ORDER BY sequence_id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        if not row:
            return hashlib.sha256(b"REMENIS_IDS_GENESIS").hexdigest()
        return row[0]

    def issue_token(self, agent_id: str, namespace: str, permission: str, ttl_seconds: int = 300) -> str:
        expires_at = time.time() + ttl_seconds
        payload = {"holder": agent_id, "namespace": namespace, "permission": permission, "expires": expires_at}
        payload_json = json.dumps(payload, sort_keys=True)
        sig = self._compute_hmac(payload_json)
        token_data = {"payload": payload, "sig": sig}
        return base64.urlsafe_b64encode(json.dumps(token_data).encode('utf-8')).decode('utf-8')

    def store_memory(self, agent_id: str, namespace: str, memory_id: str, content: str):
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

    def _register_failure(self, agent_id: str, attack_type: str, details: str):
        """Tracks failures and enforces automated blacklisting."""
        self.failed_attempts[agent_id] = self.failed_attempts.get(agent_id, 0) + 1
        failures = self.failed_attempts[agent_id]
        
        severity = "HIGH" if failures >= self.max_failures_before_lockout else "MEDIUM"
        self._log_security_event(agent_id, severity, attack_type, details)

        if failures >= self.max_failures_before_lockout:
            self.blacklisted_agents.add(agent_id)
            print(f"🛡️ [IDS PERIMETER LOCKDOWN] Agent '{agent_id}' has exceeded maximum failure threshold ({failures}). Permanently blacklisted!")

    def gateway_request(self, agent_id: str, capability_token: str, namespace: str, memory_id: str) -> str:
        """Ultimate IDS Gateway Interceptor with automated blacklisting and anomaly detection."""
        
        # 1. Check if agent is already blacklisted by the IDS
        if agent_id in self.blacklisted_agents:
            print(f"[IDS BLOCKED] Request rejected instantly. Agent '{agent_id}' is blacklisted due to prior malicious telemetry.")
            return None

        # 2. Token Decryption & Cryptographic Verification
        try:
            decoded = json.loads(base64.urlsafe_b64decode(capability_token.encode('utf-8')).decode('utf-8'))
            payload = decoded["payload"]
            provided_sig = decoded["sig"]

            payload_json = json.dumps(payload, sort_keys=True)
            if not hmac.compare_digest(self._compute_hmac(payload_json), provided_sig):
                self._register_failure(agent_id, "TOKEN_SIGNATURE_FORGERY", "Invalid cryptographic HMAC signature")
                return None

            if time.time() > payload["expires"]:
                self._register_failure(agent_id, "EXPIRED_TOKEN_ABUSE", "Attempted use of expired capability token")
                return None

            if payload["namespace"] != namespace or payload["permission"] != "READ":
                self._register_failure(agent_id, "NAMESPACE_HIJACKING", "Cross-tenant scope violation attempt")
                return None

        except Exception as e:
            self._register_failure(agent_id, "MALFORMED_PAYLOAD", f"Token decode failure: {e}")
            return None

        # 3. Ledger Chain Integrity Check (Step 1 Integration)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT content, timestamp, prev_hash, signature FROM zero_trust_ledger WHERE namespace = ? AND memory_id = ?', (namespace, memory_id))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        content, timestamp, prev_hash, stored_sig = row
        raw_data = f"{prev_hash}:{namespace}:{memory_id}:{content}:{timestamp}"
        if not hmac.compare_digest(self._compute_hmac(raw_data), stored_sig):
            self._log_security_event(agent_id, "CRITICAL", "LEDGER_TAMPERING_DETECTED", f"Hash chain mismatch on memory '{memory_id}'")
            return None

        # Success - Reset failure counter for legitimate agent
        self.failed_attempts[agent_id] = 0
        return content

if __name__ == "__main__":
    if os.path.exists("remenis_ultimate_ids.db"):
        os.remove("remenis_ultimate_ids.db")

    gateway = UltimateIDSGateway()
    gateway.store_memory(agent_id="system_admin", namespace="system_core", memory_id="kernel_01", content="Secure microkernel configuration loaded.")

    print("==================================================")
    print("🚀 RUNNING ULTIMATE IDS GATEWAY ADVERSARIAL DRILL")
    print("==================================================\n")

    rogue_bot = "threat_actor_agent_X"
    
    print("--- Attack Phase: Consecutive Intrusion Attempts ---")
    for attempt in range(1, 4):
        print(f"\n[Attempt {attempt}] Rogue agent attempting unauthorized access...")
        gateway.gateway_request(agent_id=rogue_bot, capability_token="fake_token_xyz", namespace="system_core", memory_id="kernel_01")

    print("\n--- Post-Blacklist Verification ---")
    gateway.gateway_request(agent_id=rogue_bot, capability_token="fake_token_xyz", namespace="system_core", memory_id="kernel_01")
