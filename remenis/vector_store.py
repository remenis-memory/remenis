import sqlite3
import sqlite_vec
import struct
import threading
from typing import List, Tuple

def serialize_vector(vector: List[float]) -> bytes:
    """Serializes a list of floats into raw bytes for sqlite-vec."""
    return struct.pack(f"{len(vector)}f", *vector)

class VectorStore:
    """Manages high-performance vector indexing and semantic deduplication using sqlite-vec with thread safety."""
    def __init__(self, db_path: str = "remenis.db", dimension: int = 3):
        self.db_path = db_path
        self.dimension = dimension
        # check_same_thread=False allows multi-threaded worker access safely
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_vectors USING vec0(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    embedding FLOAT[{self.dimension}]
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_metadata (
                    id INTEGER PRIMARY KEY,
                    content TEXT,
                    frame_id TEXT
                );
            """)

    def add_vector(self, frame_id: str, content: str, vector: List[float], similarity_threshold: float = 0.95) -> Tuple[bool, str]:
        """Inserts a vector if no near-duplicate semantic vector exists above the similarity threshold."""
        if len(vector) != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {len(vector)}")

        query_blob = serialize_vector(vector)
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, distance FROM memory_vectors 
            WHERE embedding MATCH ? 
            ORDER BY distance ASC 
            LIMIT 1;
        """, (query_blob,))
        
        row = cursor.fetchone()
        if row:
            distance = row[1]
            similarity = 1.0 - distance
            if similarity >= similarity_threshold:
                return False, f"DUPLICATE_REJECTED: Semantic similarity {similarity:.4f} >= threshold {similarity_threshold}"

        with self.conn:
            cursor.execute("INSERT INTO memory_vectors(embedding) VALUES (?);", (query_blob,))
            row_id = cursor.lastrowid
            cursor.execute("INSERT INTO memory_metadata(id, content, frame_id) VALUES (?, ?, ?);", (row_id, content, frame_id))

        return True, "VECTOR_INDEXED"

    def get_count(self) -> int:
        """Returns the total number of indexed vectors."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memory_vectors;")
        return cursor.fetchone()[0]
