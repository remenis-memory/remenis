import hmac
import hashlib
import time
import sqlite3
import os
import json
import base64

class RemenisAgentGateway:
    def __init__(self, db_path="remenis_gateway.db", master_secret=None):
        self.db_path = db_path
        self.master_secret = master_secret or os.environ.get("REMENIS_HMAC_KEY", "default-secure-sentinel-key-change-in-prod").encode('utf-8')
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Zero-Trust Memory Ledger
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
        
        # 2. Real-Time Security Audit & Telemetry Log Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_audit_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                agent_id TEXT NOT NULL,
                action TEXT NOT NULL,
                namespace TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _log_audit_event(self, agent_id: str, action: str, namespace: str, status: str, details: str):
        """Records immutable audit telemetry for every gateway touchpoint."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO security_audit_log (timestamp, agent_id, action, namespace, status, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (time.time(), agent_id, action, namespace, status, details))
        conn.commit()
        conn.close()

    def _compute_hmac(self, data: str) -> str:
        return hmac.new(self.master_secret, data.encode('utf-8'), hashlib.sha256).hexdigest()

    def _get_last_hash(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT signature FROM zero_trust_ledger ORDER BY sequence_id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        if not row:
            return hashlib.sha256(b"REMENIS_GATEWAY_GENESIS").hexdigest()
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
        
        self._log_audit_event(agent_id, "STORE", namespace, "SUCCESS", f"Stored memory block '{memory_id}'")
        print(f"[GATEWAY STORED] Agent '{agent_id}' anchored memory in '{namespace}'.")

    def gateway_request(self, agent_id: str, capability_token: str, namespace: str, memory_id: str) -> str:
        """
        The Core Gateway Interceptor: Validates capability tokens, checks chain 
        integrity, and logs every access attempt for real-time security telemetry.
        """
        try:
            decoded = json.loads(base64.urlsafe_b64decode(capability_token.encode('utf-8')).decode('utf-8'))
            payload = decoded["payload"]
            provided_sig = decoded["sig"]

            # 1. Verify Token Signature
            payload_json = json.dumps(payload, sort_keys=True)
            if not hmac.compare_digest(self._compute_hmac(payload_json), provided_sig):
                self._log_audit_event(agent_id, "READ", namespace, "BLOCKED", "Invalid token signature")
                print(f"[GATEWAY ALERT] Agent '{agent_id}' presented invalid signature. Access rejected.")
                return None

            # 2. Check Expiration
            if time.time() > payload["expires"]:
                self._log_audit_event(agent_id, "READ", namespace, "BLOCKED", "Expired token")
                print(f"[GATEWAY ALERT] Agent '{agent_id}' presented expired token. Access rejected.")
                return None

            # 3. Check Scope
            if payload["namespace"] != namespace or payload["permission"] != "READ":
                self._log_audit_event(agent_id, "READ", namespace, "BLOCKED", "Scope/Permission violation")
                print(f"[GATEWAY ALERT] Agent '{agent_id}' attempted scope violation on '{namespace}'. Access rejected.")
                return None

        except Exception as e:
            self._log_audit_event(agent_id, "READ", namespace, "ERROR", f"Malformed token: {e}")
            print(f"[GATEWAY ALERT] Malformed token format from agent '{agent_id}'.")
            return None

        # 4. Fetch and Verify Ledger Chain Integrity
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT content, timestamp, prev_hash, signature FROM zero_trust_ledger WHERE namespace = ? AND memory_id = ?', (namespace, memory_id))
        row = cursor.fetchone()
        conn.close()

        if not row:
            self._log_audit_event(agent_id, "READ", namespace, "NOT_FOUND", f"Memory '{memory_id}' not found")
            return None

        content, timestamp, prev_hash, stored_sig = row
        raw_data = f"{prev_hash}:{namespace}:{memory_id}:{content}:{timestamp}"
        if not hmac.compare_digest(self._compute_hmac(raw_data), stored_sig):
            self._log_audit_event(agent_id, "READ", namespace, "BREACH", f"Ledger tampering detected on '{memory_id}'")
            print(f"[CRITICAL SECURITY BREACH] Memory tampering detected for agent request!")
            return None

        # Success Telemetry
        self._log_audit_event(agent_id, "READ", namespace, "SUCCESS", f"Accessed memory '{memory_id}'")
        print(f"[GATEWAY ACCESS GRANTED] Agent '{agent_id}' successfully routed to memory in '{namespace}'.")
        return content

    def print_audit_trail(self):
        """Dumps the real-time security audit log."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, agent_id, action, namespace, status, details FROM security_audit_log ORDER BY log_id ASC')
        rows = cursor.fetchall()
        conn.close()

        print("\n==================================================")
        print("📋 REMENIS REAL-TIME SECURITY AUDIT TELEMETRY")
        print("==================================================")
        for r in rows:
            print(f"[{r[1]}] Action: {r[2]} | Namespace: {r[3]} | Status: {r[4]} | Details: {r[5]}")
        print("==================================================\n")

if __name__ == "__main__":
    if os.path.exists("remenis_gateway.db"):
        os.remove("remenis_gateway.db")

    gateway = RemenisAgentGateway()

    # 1. Store confidential memories
    gateway.store_memory(agent_id="system_admin", namespace="finance_vault", memory_id="ledger_01", content="Q4 Reserve allocation balances confirmed.")
    gateway.store_memory(agent_id="system_admin", namespace="logistics_core", memory_id="cargo_09", content="Customs manifest verified for vessel #9.")

    # 2. Issue tokens to specific agents
    token_finance = gateway.issue_token(agent_id="finance_bot_01", namespace="finance_vault", permission="READ")
    token_logistics = gateway.issue_token(agent_id="logistics_bot_02", namespace="logistics_core", permission="READ")

    print("\n--- Running Gateway Request Simulations ---")
    # Legitimate access
    gateway.gateway_request(agent_id="finance_bot_01", capability_token=token_finance, namespace="finance_vault", memory_id="ledger_01")
    
    # Blocked cross-tenant access attempt
    gateway.gateway_request(agent_id="logistics_bot_02", capability_token=token_logistics, namespace="finance_vault", memory_id="ledger_01")

    # Blocked unauthorized/forged token attempt
    gateway.gateway_request(agent_id="rogue_agent_99", capability_token="eyJmYWtlIjoidG9rZW4ifQ==", namespace="finance_vault", memory_id="ledger_01")

    # 3. Output the comprehensive security audit trail
    gateway.print_audit_trail()
