import sqlite3
import time
import math
from typing import List, Dict, Any, Optional

class MemoryEngine:
    def __init__(self, storage_path: str = "./remenis_memory.db", max_memory_mb: float = 10.0):
        self.storage_path = storage_path
        self.max_memory_mb = max_memory_mb
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            # Create main memory metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    importance REAL DEFAULT 1.0,
                    created_at REAL NOT NULL
                )
            """)
            # Create FTS5 virtual table for full-text search
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    content,
                    content='memories',
                    content_rowid='id'
                )
            """)
            conn.commit()

    def store(self, content: str, importance: float = 1.0) -> int:
        now = time.time()
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (content, importance, created_at) VALUES (?, ?, ?)",
                (content, importance, now)
            )
            memory_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO memory_fts(rowid, content) VALUES (?, ?)",
                (memory_id, content)
            )
            conn.commit()
            return memory_id

    def recall(self, query: str, limit: int = 5, decay_rate: float = 0.01) -> List[Dict[str, Any]]:
        """
        Recalls relevant memories using FTS5 search combined with recency decay.
        - decay_rate: Controls how quickly memories lose score over time (in hours).
        """
        now = time.time()
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            # Query FTS5 for initial search relevance scores
            cursor.execute("""
                SELECT m.id, m.content, m.importance, m.created_at, bm25(memory_fts) AS raw_rank
                FROM memory_fts f
                JOIN memories m ON f.rowid = m.id
                WHERE memory_fts MATCH ?
            """, (query,))
            
            rows = cursor.fetchall()

        results = []
        for memory_id, content, importance, created_at, raw_rank in rows:
            # FTS5 bm25 returns lower negative numbers for better matches, convert to a positive score
            base_score = max(0.1, -raw_rank)
            
            # Calculate age in hours
            age_hours = (now - created_at) / 3600.0
            
            # Apply exponential decay based on age
            time_decay = math.exp(-decay_rate * age_hours)
            
            # Combine text relevance, user importance weighting, and time decay
            final_score = round(base_score * importance * time_decay, 4)

            results.append({
                "id": memory_id,
                "content": content,
                "importance": importance,
                "score": final_score,
                "created_at": created_at
            })

        # Sort results by final decaying score in descending order
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
