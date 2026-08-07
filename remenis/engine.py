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

    def store(self, content: str, importance: float = 1.0) -> List[int]:
        facts = self.extractor.extract_facts(content)
        inserted_ids = []
        
        for fact in facts:
            # Check for potential conflicts against existing memories
            existing = self.recall(fact, top_k=5)
            conflicts = self.extractor.resolve_conflicts(fact, existing)
            
            now = time.time()
            vector = self._text_to_vector(fact)
            serialized_vec = self._serialize_vector(vector)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Overwrite/delete conflicting old memories if found
                if conflicts:
                    cursor.execute(f"DELETE FROM memories WHERE id IN ({','.join('?'*len(conflicts))})", conflicts)
                    cursor.execute(f"DELETE FROM memory_vectors WHERE memory_id IN ({','.join('?'*len(conflicts))})", conflicts)

                cursor.execute(
                    "INSERT INTO memories (content, importance, created_at) VALUES (?, ?, ?)",
                    (fact, importance, now)
                )
                memory_id = cursor.lastrowid
                
                cursor.execute(
                    "INSERT INTO memory_vectors(memory_id, embedding) VALUES (?, ?)",
                    (memory_id, serialized_vec)
                )
                conn.commit()
                inserted_ids.append(memory_id)
                
        return inserted_ids

    def recall(self, query: str, top_k: int = 3, decay_rate: float = 0.01) -> List[Dict[str, Any]]:
        query_vec = self._serialize_vector(self._text_to_vector(query))
        now = time.time()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    m.id, 
                    m.content, 
                    m.importance, 
                    m.created_at, 
                    v.distance
                FROM memory_vectors v
                JOIN memories m ON m.id = v.memory_id
                WHERE embedding MATCH ? AND k = ?
            """, (query_vec, top_k))

            results = []
            for row in cursor.fetchall():
                mem_id, content, importance, created_at, distance = row
                
                similarity = 1.0 / (1.0 + distance)
                age_days = (now - created_at) / 86400.0
                time_decay = math.exp(-decay_rate * age_days)

                final_score = similarity * importance * time_decay

                results.append({
                    "id": mem_id,
                    "content": content,
                    "similarity": round(similarity, 4),
                    "final_score": round(final_score, 4)
                })

            results.sort(key=lambda x: x["final_score"], reverse=True)
            return results

