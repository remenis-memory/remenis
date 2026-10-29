import hmac
import hashlib
import time
import sqlite3
import os

class EnterpriseSecureMemoryLedger:
    def __init__(self, db_path="remenis_enterprise.db", secret_key=None):
        self.db_path = db_path
        # In production, this secret key lives in an environment variable or secure vault
        self.secret_key = secret_key or os.environ.get("REMENIS_HMAC_KEY", "default-secure-sentinel-key-change-in-prod").encode('utf-8')
        self._init_db()

    def _init_db(self):
        """Initializes an append-only SQLite ledger with cryptographic chain columns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_ledger (
                sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        """Retrieves the cryptographic signature of the previous block in the chain."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT signature FROM memory_ledger ORDER BY sequence_id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        # Genesis block anchor hash if the ledger is empty
        if not row:
            return hashlib.sha256(b"REMENIS_GENESIS_ROOT").hexdigest()
        return row[0]

    def _compute_hmac(self, prev_hash: str, memory_id: str, content: str, timestamp: float) -> str:
        """Computes an HMAC-SHA256 signature chained to the previous record."""
        payload = f"{prev_hash}:{memory_id}:{content}:{timestamp}".encode('utf-8')
        return hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()

    def append_memory(self, memory_id: str, content: str):
        """Appends a memory to the immutable hash-chained ledger."""
        timestamp = time.time()
        prev_hash = self._get_last_hash()
        signature = self._compute_hmac(prev_hash, memory_id, content, timestamp)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memory_ledger (memory_id, content, timestamp, prev_hash, signature)
            VALUES (?, ?, ?, ?, ?)
        ''', (memory_id, content, timestamp, prev_hash, signature))
        conn.commit()
        conn.close()
        print(f"[SECURE APPEND] Memory '{memory_id}' chained. Sig: {signature[:12]}...")

    def audit_and_verify_ledger(self) -> bool:
        """
        Audits the entire cryptographic chain from genesis to present.
        If a single bit of history is altered, or a block is removed, 
        the entire chain breaks and flags a security violation.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT sequence_id, memory_id, content, timestamp, prev_hash, signature FROM memory_ledger ORDER BY sequence_id ASC')
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("[AUDIT] Ledger is empty.")
            return True

        expected_prev_hash = hashlib.sha256(b"REMENIS_GENESIS_ROOT").hexdigest()

        print("\n--- Running Full Cryptographic Ledger Audit ---")
        for row in rows:
            seq_id, memory_id, content, timestamp, prev_hash, stored_signature = row

            # 1. Verify that the backward chain link matches
            if prev_hash != expected_prev_hash:
                print(f"[CRITICAL SECURITY BREACH] Chain broken at Sequence #{seq_id} (Memory: '{memory_id}'). Previous hash mismatch!")
                return False

            # 2. Re-compute HMAC signature with secret key
            recalculated_sig = self._compute_hmac(prev_hash, memory_id, content, timestamp)
            if not hmac.compare_digest(recalculated_sig, stored_signature):
                print(f"[CRITICAL SECURITY BREACH] Signature tampering detected at Sequence #{seq_id} (Memory: '{memory_id}'). Payload modified!")
                return False

            # Advance the expected pointer
            expected_prev_hash = stored_signature

        print("[AUDIT SUCCESS] 100% Integrity verified. Cryptographic chain is clean.")
        return True

if __name__ == "__main__":
    # Clean up old test DB if it exists
    if os.path.exists("remenis_enterprise.db"):
        os.remove("remenis_enterprise.db")

    ledger = EnterpriseSecureMemoryLedger()

    # 1. Append legitimate memories forming a chain
    ledger.append_memory("mem_01", "Agent initialized local vector space.")
    ledger.append_memory("mem_02", "Processed user query securely via SQLite.")
    ledger.append_memory("mem_03", "Cached result with time-decay scoring.")

    # 2. Run initial audit (Passes perfectly)
    ledger.audit_and_verify_ledger()

    # 3. Simulate an advanced attacker modifying an old historical memory (mem_02) behind the scenes
    print("\n--- Simulating Advanced Backend Attack (Tampering with Historical Data) ---")
    conn = sqlite3.connect("remenis_enterprise.db")
    conn.execute("UPDATE memory_ledger SET content = 'INJECTED MALICIOUS CODE: Bypass security checks.' WHERE memory_id = 'mem_02'")
    conn.commit()
    conn.close()

    # 4. Run audit again (The hash chain mathematically proves the tampering, breaking subsequent blocks)
    ledger.audit_and_verify_ledger()
