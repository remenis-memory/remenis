import sqlite3
import sqlite_vec
import time
import math
import struct
from typing import List, Dict, Any

class MemoryEngine:
    def __init__(self, storage_path: str = "./remenis_memory.db", vector_dim: int = 16):
        self.storage_path = storage_path
        self.vector_dim = vector_dim
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.storage_path)
        # Enable sqlite-vec extension
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Table 1: Standard memory details
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    importance REAL DEFAULT 1.0,
                    created_at REAL NOT NULL
                )
            """)
            # Table 2: Vector embeddings table (using sqlite-vec)
            cursor.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_vectors USING vec0(
                    memory_id INTEGER PRIMARY KEY,
                    embedding float[{self.vector_dim}]
                )
            """)
            conn.commit()

    def _text_to_vector(self, text: str) -> List[float]:
        """
        Converts text into a vector coordinate representation.
        (This will be connected to a dedicated local embedding model in Step 2).
        """
        words = text.lower().split()
        vector = [0.0] * self.vector_dim
        for word in words:
            for i, char in enumerate(word):
                vector[i % self.vector_dim] += ord(char) % 10 / 10.0
        
        # Normalize vector length
        magnitude = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / magnitude for v in vector]

    def _serialize_vector(self, vector: List[float]) -> bytes:
        """Packs a float list into binary format for sqlite-vec."""
        return struct.pack(f"{len(vector)}f", *vector)

    def store(self, content: str, importance: float = 1.0) -> int:
        now = time.time()
        vector = self._text_to_vector(content)
        serialized_vec = self._serialize_vector(vector)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (content, importance, created_at) VALUES (?, ?, ?)",
                (content, importance, now)
            )
            memory_id = cursor.lastrowid
            
            cursor.execute(
                "INSERT INTO memory_vectors(memory_id, embedding) VALUES (?, ?)",
                (memory_id, serialized_vec)
            )
            conn.commit()
            return memory_id

