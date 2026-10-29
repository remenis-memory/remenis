import os
import sqlite3
from typing import List, Dict, Any, Tuple
from .vector_store import VectorStore
from .sentinel import RemenisSentinel
from .retriever import MemoryRetriever

class RemenisEngine:
    def __init__(self, db_path="remenis.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.vector_store = VectorStore(db_path)
        self.sentinel = RemenisSentinel()
        self.retriever = MemoryRetriever()

    def audit_inspect(self):
        print("🛡️ [AUDIT INSPECT]: Inspecting memory database and security trails...")
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        print(f"  └─ Total stored memories in database: {count}")

    def store_memory(
        self,
        content: str,
        task_intent: str = "",
        vector: List[float] = None,
        origin_type: str = "agent_action",
        similarity_threshold: float = 0.95,
        category: str = "general"
    ) -> Tuple[bool, str]:
        passed, audit_msg, frame = self.sentinel.audit_and_commit(content)
        if not passed or frame is None:
            return False, f"REJECTED: {audit_msg}"
        return True, "COMMITTED"
