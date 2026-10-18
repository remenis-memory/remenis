import hmac
import hashlib
import time
import sqlite3
import os

class ScopedEnterpriseLedger:
    def __init__(self, db_path="remenis_scoped_ledger.db", secret_key=None):
        self.db_path = db_path
        self.secret_key = secret_key or os.environ.get("REMENIS_HMAC_KEY", "default-secure-sentinel-key-change-in-prod").encode('utf-8')
        self._init_db()

    def _init_db(self):
        """Initializes SQLite with agent identity columns and cryptographic chain linkage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scoped_ledger (
                sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                scope_role TEXT NOT NULL,
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
        """Retrieves the last signature across the entire global ledger to maintain chain continuity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT signature FROM scoped_ledger ORDER BY sequence_id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return hashlib.sha256(b"REMENIS_SCOPED_GENESIS").hexdigest()
        return row[0]

    def _compute_hmac(self, prev_hash: str, agent_id: str, scope_role: str, memory_id: str, content: str, timestamp: float) -> str:
        """Computes an HMAC signature bound to identity, role, and historical chain hash."""
        payload = f"{prev_hash}:{agent_id}:{scope_role}:{memory_id}:{content}:{timestamp}".encode('utf-8')
        return hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()

    def append_memory(self, agent_id: str, scope_role: str, memory_id: str, content: str):
        """Appends a memory securely bound to a non-human identity."""
        timestamp = time.time()
        prev_hash = self._get_last_hash()
        signature = self._compute_hmac(prev_hash, agent_id, scope_role, memory_id, content, timestamp)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scoped_ledger (agent_id, scope_role, memory_id, content, timestamp, prev_hash, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (agent_id, scope_role, memory_id, content, timestamp, prev_hash, signature))
        conn.commit()
        conn.close()
        print(f"[STORED] Agent '{agent_id}' ({scope_role}) secured memory '{memory_id}'.")

    def retrieve_memory(self, requesting_agent_id: str, requesting_role: str, target_agent_id: str, memory_id: str) -> str:
        """
        Retrieves a memory with strict Identity & Role-Based Access Control (RBAC) 
        plus cryptographic signature verification.
        """
        # 1. Access Control Boundary Check
        if requesting_agent_id != target_agent_id and requesting_role != "admin":
            print(f"\n[SECURITY BREACH BLOCKED] Agent '{requesting_agent_id}' (Role: {requesting_role}) "
                  f"attempted unauthorized read of memory belonging to '{target_agent_id}'!")
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sequence_id, agent_id, scope_role, content, timestamp, prev_hash, signature 
            FROM scoped_ledger 
            WHERE agent_id = ? AND memory_id = ?
        ''', (target_agent_id, memory_id))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        seq_id, agent_id, scope_role, content, timestamp, prev_hash, stored_signature = row

        # 2. Cryptographic Integrity Validation
        recalculated_sig = self._compute_hmac(prev_hash, agent_id, scope_role, memory_id, content, timestamp)
        if not hmac.compare_digest(recalculated_sig, stored_signature):
            print(f"[SECURITY ALERT] Tampering detected on memory '{memory_id}' for agent '{target_agent_id}'! Dropping frame.")
            return None

        print(f"[ACCESS GRANTED] Agent '{requesting_agent_id}' successfully accessed verified memory '{memory_id}'.")
        return content

if __name__ == "__main__":
    if os.path.exists("remenis_scoped_ledger.db"):
        os.remove("remenis_scoped_ledger.db")

    ledger = ScopedEnterpriseLedger()

    # 1. Different agents store memories in their respective namespaces
    ledger.append_memory(agent_id="logistics_agent_01", scope_role="worker", memory_id="manifest_09", content="Shipment #9 cleared customs at port.")
    ledger.append_memory(agent_id="support_agent_02", scope_role="worker", memory_id="ticket_42", content="Customer requested refund for order #102.")

    # 2. Legitimate Self-Read (Agent reads its own memory)
    print("\n--- Test 1: Legitimate Self-Read ---")
    ledger.retrieve_memory(
        requesting_agent_id="logistics_agent_01", 
        requesting_role="worker", 
        target_agent_id="logistics_agent_01", 
        memory_id="manifest_09"
    )

    # 3. Unauthorized Cross-Agent Read (Support agent tries to spy on logistics)
    print("\n--- Test 2: Unauthorized Cross-Agent Espionage ---")
    ledger.retrieve_memory(
        requesting_agent_id="support_agent_02", 
        requesting_role="worker", 
        target_agent_id="logistics_agent_01", 
        memory_id="manifest_09"
    )

    # 4. System Admin Override Read
    print("\n--- Test 3: System Admin Authorized Override ---")
    ledger.retrieve_memory(
        requesting_agent_id="system_root", 
        requesting_role="admin", 
        target_agent_id="logistics_agent_01", 
        memory_id="manifest_09"
    )
