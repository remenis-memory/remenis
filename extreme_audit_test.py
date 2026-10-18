import hmac
import hashlib
import time
import sqlite3
import os

class EnterpriseSecureMemoryLedger:
    def __init__(self, db_path="remenis_brutal_test.db", secret_key=None):
        self.db_path = db_path
        self.secret_key = secret_key or os.environ.get("REMENIS_HMAC_KEY", "default-secure-sentinel-key-change-in-prod").encode('utf-8')
        self._init_db()

    def _init_db(self):
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT signature FROM memory_ledger ORDER BY sequence_id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        if not row:
            return hashlib.sha256(b"REMENIS_GENESIS_ROOT").hexdigest()
        return row[0]

    def _compute_hmac(self, prev_hash: str, memory_id: str, content: str, timestamp: float) -> str:
        payload = f"{prev_hash}:{memory_id}:{content}:{timestamp}".encode('utf-8')
        return hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()

    def append_memory(self, memory_id: str, content: str):
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

    def audit_and_verify_ledger(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT sequence_id, memory_id, content, timestamp, prev_hash, signature FROM memory_ledger ORDER BY sequence_id ASC')
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("[AUDIT FAILED] Ledger is completely empty.")
            return False

        expected_prev_hash = hashlib.sha256(b"REMENIS_GENESIS_ROOT").hexdigest()

        for row in rows:
            seq_id, memory_id, content, timestamp, prev_hash, stored_signature = row

            if prev_hash != expected_prev_hash:
                print(f"[BREACH CAUGHT] Broken chain link at Sequence #{seq_id} ('{memory_id}'). Expected prev_hash does not match.")
                return False

            recalculated_sig = self._compute_hmac(prev_hash, memory_id, content, timestamp)
            if not hmac.compare_digest(recalculated_sig, stored_signature):
                print(f"[BREACH CAUGHT] Signature mismatch at Sequence #{seq_id} ('{memory_id}'). Payload or signature altered.")
                return False

            expected_prev_hash = stored_signature

        return True

def run_extreme_tests():
    db_file = "remenis_brutal_test.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    ledger = EnterpriseSecureMemoryLedger(db_path=db_file)

    # Populate initial clean state
    ledger.append_memory("block_A", "Initial system boot sequence verified.")
    ledger.append_memory("block_B", "Loaded agent memory vector index.")
    ledger.append_memory("block_C", "Established secure communication tunnel.")

    print("=== BASELINE TEST ===")
    assert ledger.audit_and_verify_ledger() == True, "Baseline audit failed!"
    print("[PASS] Baseline clean ledger passed audit.\n")

    # --- TEST 1: The Pruning Attack (Deleting Genesis/First Block) ---
    print("=== TEST 1: Deleting First Block (Pruning Attack) ===")
    conn = sqlite3.connect(db_file)
    conn.execute("DELETE FROM memory_ledger WHERE memory_id = 'block_A'")
    conn.commit()
    conn.close()

    result = ledger.audit_and_verify_ledger()
    assert result == False, "Ledger failed to catch deleted block!"
    print("[PASS] Successfully caught missing block and flagged breach.\n")

    # Reset for next test
    if os.path.exists(db_file):
        os.remove(db_file)
    ledger = EnterpriseSecureMemoryLedger(db_path=db_file)
    ledger.append_memory("block_A", "Initial system boot sequence verified.")
    ledger.append_memory("block_B", "Loaded agent memory vector index.")
    ledger.append_memory("block_C", "Established secure communication tunnel.")

    # --- TEST 2: The Re-ordering Attack (Swapping Blocks) ---
    print("=== TEST 2: Re-ordering Blocks (Row Swapping Attack) ===")
    conn = sqlite3.connect(db_file)
    # Swap contents/signatures or IDs of block_B and block_C
    conn.execute("UPDATE memory_ledger SET memory_id = 'temp' WHERE memory_id = 'block_B'")
    conn.execute("UPDATE memory_ledger SET memory_id = 'block_B' WHERE memory_id = 'block_C'")
    conn.execute("UPDATE memory_ledger SET memory_id = 'block_C' WHERE memory_id = 'temp'")
    conn.commit()
    conn.close()

    result = ledger.audit_and_verify_ledger()
    assert result == False, "Ledger failed to catch re-ordered blocks!"
    print("[PASS] Successfully caught block re-ordering and flagged breach.\n")

    print("=== ALL EXTREME ATTACK VECTORS NEUTRALIZED ===" )

if __name__ == "__main__":
    run_extreme_tests()
