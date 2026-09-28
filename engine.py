import sqlite3
import sqlite_vec
import struct
import json
from datetime import datetime, timezone
from guardrails import GuardrailEngine, SecurityViolationError
from scoring import DeterministicScorer

class RemenisEngine:
    def __init__(self, db_path="remenis.db"):
        self.db_path = db_path
        self.guardrails = GuardrailEngine()
        self.scorer = DeterministicScorer()
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)

        # Create memories table with vector support
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_text TEXT NOT NULL,
                category TEXT NOT NULL,
                importance REAL DEFAULT 1.0,
                created_at TEXT NOT NULL
            );
        """)
        self.conn.commit()

    def store_memory(self, fact_text: str, category: str = "general", importance: float = 1.0):
        """
        Stores a memory after passing through the GuardrailEngine kill-switch.
        """
        # 1. Enforce Guardrails (State Isolation)
        self.guardrails.validate_memory(fact_text, category)

        # 2. Insert into SQLite
        now_str = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO memories (fact_text, category, importance, created_at) VALUES (?, ?, ?, ?)",
            (fact_text, category, importance, now_str)
        )
        self.conn.commit()
        print(f"🛡️ [SECURE STORED] Category: '{category}' | Fact: '{fact_text}'")

    def audit_inspect(self):
        """
        Local Auditability: Dumps the entire plain-text SQLite database state.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, fact_text, category, importance, created_at FROM memories")
        rows = cursor.fetchall()
        
        print("\n" + "="*50)
        print("🔍 REMENIS LOCAL AUDIT INSPECTOR (100% Transparent State)")
        print("="*50)
        if not rows:
            print("Database is currently empty.")
        for row in rows:
            print(f"ID: {row[0]} | Cat: {row[2]} | Imp: {row[3]} | Time: {row[4]}")
            print(f" └─ Fact: {row[1]}")
        print("="*50 + "\n")

if __name__ == "__main__":
    engine = RemenisEngine()
    print("Remenis Local Engine Initialized with sqlite-vec.")
