import sqlite3
from typing import List, Dict, Any, Optional

class MemoryEngine:
    """
    Lightweight, sub-gigabyte long-term memory engine for local AI agents.
    """
    def __init__(self, storage_path: str = "./agent_memory.db", max_memory_mb: int = 500):
        self.storage_path = storage_path
        self.max_memory_mb = max_memory_mb
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite schema for memory storage."""
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def store(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Store a new memory item."""
        import json
        meta_json = json.dumps(metadata) if metadata else None
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (content, metadata) VALUES (?, ?)",
                (content, meta_json)
            )
            conn.commit()
            return cursor.lastrowid

    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recall relevant memories matching a query string."""
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, metadata, created_at FROM memories WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
                (f"%{query}%", limit)
            )
            rows = cursor.fetchall()
            return [
                {"id": r[0], "content": r[1], "metadata": r[2], "created_at": r[3]}
                for r in rows
            ]
