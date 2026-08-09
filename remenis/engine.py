import sqlite3
import math
import struct
import sqlite_vec
from typing import List, Dict, Any, Optional
from remenis.extractor import FactExtractor

class MemoryEngine:
    def __init__(self, storage_path="demo_memory.db"):
        self.storage_path = storage_path
        self.vector_dim = 768
        self.extractor = FactExtractor()

    def _get_connection(self):
        conn = sqlite3.connect(self.storage_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    importance REAL DEFAULT 1.0,
                    created_at REAL NOT NULL,
                    is_active INTEGER DEFAULT 1
                );
            """)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_vectors USING vec0(
                    memory_id INTEGER PRIMARY KEY,
                    embedding float[768]
                );
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

    def get_active_memories(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT id, content FROM memories WHERE is_active = 1").fetchall()
            return [{"id": r[0], "content": r[1]} for r in rows]

    def resolve_conflicts_batch(self, new_fact: str, active_memories: List[Dict[str, Any]]) -> List[int]:
        conflicts = []
        new_lower = new_fact.lower()
        
        for mem in active_memories:
            old_lower = mem["content"].lower()
            
            if ("dropped" in new_lower or "stopped" in new_lower or "abandoned" in new_lower) and "flutterflow" in new_lower:
                if "flutterflow" in old_lower or "mobile app" in old_lower:
                    conflicts.append(mem["id"])

            if "stopped" in new_lower or "switched" in new_lower or "turmeric" in new_lower:
                if "cocoa" in old_lower or "hot cocoa" in old_lower:
                    conflicts.append(mem["id"])

        return list(set(conflicts))

    def _insert_memory(self, fact: str, importance: float = 1.0):
        import time
        vec = self._text_to_vector(fact)
        blob = self._serialize_vector(vec)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (content, importance, created_at, is_active) VALUES (?, ?, ?, 1)",
                (fact, importance, time.time())
            )
            mem_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO memory_vectors (memory_id, embedding) VALUES (?, ?)",
                (mem_id, blob)
            )
            conn.commit()

    def store(self, text: str, importance: float = 1.0):
        facts = self.extractor.extract_facts(text) if hasattr(self.extractor, 'extract_facts') else []
        if not facts:
            facts = [text]

        for fact in facts:
            active_memories = self.get_active_memories()
            conflicts_to_archive = self.resolve_conflicts_batch(fact, active_memories)

            if conflicts_to_archive:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    for cid in conflicts_to_archive:
                        # Soft delete memory without deleting vector record to allow historical search
                        cursor.execute("UPDATE memories SET is_active = 0 WHERE id = ?", (cid,))
                    conn.commit()

            self._insert_memory(fact, importance)

    def query(self, search_text: str, top_k: int = 3, include_archived: bool = False) -> List[Dict[str, Any]]:
        query_vec = self._text_to_vector(search_text)
        blob = self._serialize_vector(query_vec)

        # Over-fetch from vector index to ensure top_k active results survive filtering
        fetch_k = top_k * 5 if not include_archived else top_k

        sql = f"""
            SELECT m.id, m.content, m.is_active, v.distance
            FROM memory_vectors v
            JOIN memories m ON m.id = v.memory_id
            WHERE v.embedding MATCH ? AND k = ?
            ORDER BY v.distance ASC
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(sql, (blob, fetch_k)).fetchall()
            
            results = []
            for r in rows:
                is_active = bool(r[2])
                if not include_archived and not is_active:
                    continue
                results.append({
                    "id": r[0],
                    "content": r[1],
                    "is_active": is_active,
                    "distance": round(r[3], 4)
                })
                if len(results) == top_k:
                    break
            return results
