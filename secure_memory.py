import hashlib
import time
import sqlite3

class SecureMemoryStore:
    def __init__(self, db_path="remenis.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes SQLite table with a provenance hash column."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                provenance_hash TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _generate_hash(self, memory_id: str, content: str, timestamp: float) -> str:
        """Generates a cryptographic SHA-256 seal for the memory frame."""
        raw_data = f"{memory_id}:{content}:{timestamp}"
        return hashlib.sha256(raw_data.encode('utf-8')).hexdigest()

    def store_memory(self, memory_id: str, content: str):
        """Writes a memory frame with an immutable cryptographic seal."""
        timestamp = time.time()
        provenance_hash = self._generate_hash(memory_id, content, timestamp)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO memories (id, content, timestamp, provenance_hash)
            VALUES (?, ?, ?, ?)
        ''', (memory_id, content, timestamp, provenance_hash))
        conn.commit()
        conn.close()
        print(f"[STORED] Memory '{memory_id}' sealed with hash: {provenance_hash[:12]}...")

    def retrieve_and_verify(self, memory_id: str) -> str:
        """Retrieves a memory and validates its SHA-256 integrity seal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT content, timestamp, provenance_hash FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        content, timestamp, stored_hash = row

        # Re-calculate the hash to verify integrity
        calculated_hash = self._generate_hash(memory_id, content, timestamp)

        if calculated_hash != stored_hash:
            print(f"[SECURITY ALERT] Tampering detected on memory '{memory_id}'! Dropping frame.")
            return None  # Drop compromised memory instantly

        return content

if __name__ == "__main__":
    # Initialize our secure memory engine
    db = SecureMemoryStore()

    # 1. Store a legitimate memory
    db.store_memory("user_pref_01", "User prefers local-first SQLite architecture.")

    # 2. Retrieve it normally (Passes verification)
    safe_memory = db.retrieve_and_verify("user_pref_01")
    print(f"Retrieved Clean Memory: {safe_memory}\n")

    # 3. Simulate an attacker modifying the database directly behind our back
    print("--- Simulating Database Tampering ---")
    conn = sqlite3.connect("remenis.db")
    conn.execute("UPDATE memories SET content = 'User prefers cloud-managed remote databases with zero privacy.' WHERE id = 'user_pref_01'")
    conn.commit()
    conn.close()

    # 4. Try to retrieve it again (Triggers the tamper check and drops it)
    compromised_memory = db.retrieve_and_verify("user_pref_01")
    print(f"Result after tampering: {compromised_memory}")
