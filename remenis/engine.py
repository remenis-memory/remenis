import sqlite3
import sqlite_vec
import time
import math
import struct
from typing import List, Dict, Any
from remenis.extractor import FactExtractor

class MemoryEngine:
    def __init__(self, storage_path: str = "./remenis_memory.db", vector_dim: int = 16):
        self.storage_path = storage_path
        self.vector_dim = vector_dim
        self.extractor = FactExtractor()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.storage_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    importance REAL DEFAULT 1.0,
                    created_at REAL NOT NULL
                )
            """)
            cursor.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_vectors USING vec0(
                    memory_id INTEGER PRIMARY KEY,
                    embedding float[{self.vector_dim}]
                )
            """)
            conn.commit()

    def _text_to_vector(self, text: str) -> List[float]:
        words = text.lower().split()
        vector = [0.0] * self.vector_dim
        for word in words:
            for i, char in enumerate(word):
                vector[i % self.vector_dim] += ord(char) % 10 / 10.0
        
        magnitude = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / magnitude for v in vector]

    def _serialize_vector(self, vector: List[float]) -> bytes:
        return struct.pack(f"{len(vector)}f", *vector)

    def store(self, text: str, importance: float = 1.0) -> list[int]:
        facts = self.extractor.extract_facts(text)
        
        # 1. Fetch existing memories using the helper connection
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content FROM memories")
            existing = [{"id": row[0], "content": row[1]} for row in cursor.fetchall()]

        # 2. Batch resolve conflicts in one API call
        conflicts_to_delete = self.extractor.resolve_conflicts_batch(facts, existing)
        
        # 3. Delete conflicting entries from both tables
        if conflicts_to_delete:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for cid in conflicts_to_delete:
                    cursor.execute("DELETE FROM memories WHERE id = ?", (cid,))
                    cursor.execute("DELETE FROM memory_vectors WHERE memory_id = ?", (cid,))
                conn.commit()

        # 4. Insert new facts into both tables
        stored_ids = []
        now = time.time()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for fact in facts:
                # Insert memory text and metadata
                cursor.execute(
                    "INSERT INTO memories (content, importance, created_at) VALUES (?, ?, ?)",
                    (fact, importance, now)
                )
                memory_id = cursor.lastrowid

                # Generate vector embedding and store in sqlite-vec table
                vector = self._text_to_vector(fact)
                serialized_vector = self._serialize_vector(vector)
                
                cursor.execute(
                    "INSERT INTO memory_vectors (memory_id, embedding) VALUES (?, ?)",
                    (memory_id, serialized_vector)
                )

                stored_ids.append(memory_id)
            conn.commit()

        return stored_ids
        
