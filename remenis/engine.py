import json
import os
import sqlite3
import time
from typing import List, Dict, Any, Optional

class MemoryEngine:
    """
    Lightweight, sub-gigabyte long-term memory middleware for AI agents.
    Uses SQLite FTS5 for fast local retrieval and enforces strict disk quotas.
    """
    def __init__(self, storage_path: str = "./agent_memory.db", max_memory_mb: int = 500):
        self.storage_path = storage_path
        self.max_memory_mb = max_memory_mb
        self._init_db()
        self._enforce_storage_limit()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.storage_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize main storage and FTS5 full-text search virtual table."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Base table for structured memory metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    importance REAL DEFAULT 1.0,
                    metadata TEXT,
                    created_at REAL NOT NULL
                )
            """)
            
            # FTS5 table for fast local full-text search
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    content,
                    content='memories',
                    content_rowid='id'
                )
            """)
            
            # Triggers to keep FTS table automatically synchronized
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, content) VALUES('delete', old.id, old.content);
                END;
            """)
            conn.commit()

    def _enforce_storage_limit(self) -> None:
        """Enforces the sub-gigabyte max_memory_mb limit by purging oldest low-importance records."""
        if not os.path.exists(self.storage_path):
            return

        max_bytes = self.max_memory_mb * 1024 * 1024
        current_size = os.path.getsize(self.storage_path)

        if current_size > max_bytes:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Delete bottom 10% lowest importance / oldest memories to reclaim disk space
                cursor.execute("""
                    DELETE FROM memories 
                    WHERE id IN (
                        SELECT id FROM memories 
                        ORDER BY importance ASC, created_at ASC 
                        LIMIT (SELECT COUNT(*) / 10 FROM memories)
                    )
                """)
                conn.commit()
                cursor.execute("VACUUM")

    def store(self, content: str, importance: float = 1.0, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Store a new memory item with an importance score and optional metadata."""
        meta_json = json.dumps(metadata) if metadata else None
        created_at = time.time()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (content, importance, metadata, created_at) VALUES (?, ?, ?, ?)",
                (content, importance, meta_json, created_at)
            )
            conn.commit()
            memory_id = cursor.lastrowid

        self._enforce_storage_limit()
        return memory_id

    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recall relevant memories matching a query string using FTS5 ranking
        combined with importance and recency decay.
        """
        cleaned_query = "".join(c for c in query if c.isalnum() or c.isspace()).strip()
        if not cleaned_query:
            return []

        # Convert simple phrase query to FTS matching format
        fts_query = " OR ".join(cleaned_query.split())

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.id, m.content, m.importance, m.metadata, m.created_at, fts.rank
                FROM memories_fts fts
                JOIN memories m ON m.id = fts.rowid
                WHERE memories_fts MATCH ?
                ORDER BY (fts.rank * m.importance) ASC
                LIMIT ?
            """, (fts_query, limit))
            
            rows = cursor.fetchall()
            
            results = []
            for r in rows:
                results.append({
                    "id": r["id"],
                    "content": r["content"],
                    "importance": r["importance"],
                    "metadata": json.loads(r["metadata"]) if r["metadata"] else None,
                    "created_at": r["created_at"],
                    "score": round(abs(r["rank"]), 4)
                })
            return results
