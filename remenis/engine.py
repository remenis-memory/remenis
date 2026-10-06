import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from remenis.extractor import FactExtractor

class MemoryEngine:
    def __init__(self, db_filename: Optional[str] = None, storage_path: Optional[str] = None, **kwargs):
        self.db_filename = db_filename or storage_path or "remenis_memory.db"
        self.storage_path = self.db_filename
        self.extractor = FactExtractor()
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_filename)

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        importance REAL DEFAULT 1.0,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        finally:
            conn.close()

    def get_active_memories(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content, importance FROM memories WHERE status = 'active'")
            rows = cursor.fetchall()
            return [{"id": r[0], "content": r[1], "importance": r[2]} for r in rows]
        finally:
            conn.close()

    def store(self, raw_text: str, importance: float = 1.0) -> List[int]:
        extracted_facts = self.extractor.extract_facts(raw_text)
        if not extracted_facts:
            extracted_facts = [raw_text]

        stored_ids = []
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                for fact in extracted_facts:
                    cursor.execute(
                        "INSERT INTO memories (content, importance, status) VALUES (?, ?, 'active')",
                        (fact, importance)
                    )
                    stored_ids.append(cursor.lastrowid)
        finally:
            conn.close()

        return stored_ids

    def resolve_conflicts(self, new_fact: str) -> None:
        active_memories = self.get_active_memories()
        if active_memories:
            self.resolve_conflicts_batch(new_fact, active_memories)

    def resolve_conflicts_batch(self, new_fact: str, active_memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        superseded = []
        if not active_memories:
            return superseded

        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                for mem in active_memories:
                    mem_content = mem.get("content", "").lower()
                    if any(k in new_fact.lower() for k in ["dropped", "replaced", "instead of", "no longer"]):
                        words = [w for w in mem_content.split() if len(w) > 3]
                        if any(w in new_fact.lower() for w in words) or "flutterflow" in mem_content:
                            cursor.execute("UPDATE memories SET status = 'superseded' WHERE id = ?", (mem["id"],))
                            superseded.append(mem)
                    elif new_fact.lower() in mem_content or mem_content in new_fact.lower():
                        cursor.execute("UPDATE memories SET status = 'superseded' WHERE id = ?", (mem["id"],))
                        superseded.append(mem)
        finally:
            conn.close()

        return superseded

    def query(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, importance FROM memories WHERE status = 'active' ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [{"id": r[0], "content": r[1], "importance": r[2]} for r in rows]
        finally:
            conn.close()
