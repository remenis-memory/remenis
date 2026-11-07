import struct
import zlib
import json
import sqlite3
import numpy as np

class RemenisLSEREngine:
    MAGIC_HEADER = b"RMNS"  # Proprietary file identifier signature
    VERSION = 1

    def __init__(self, db_path="remenis.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lser_vectors (
                    key TEXT PRIMARY KEY,
                    compressed_payload BLOB,
                    vector_blob BLOB,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def pack_state(self, key: str, payload: dict, vector: list[float]) -> bytes:
        """
        Compresses structured context into hyper-dense .rmns binary format.
        Structure: [HEADER 4b][VERSION 2b][PAYLOAD_LEN 4b][PAYLOAD_BLOB][VECTOR_BLOB]
        """
        json_bytes = json.dumps(payload).encode("utf-8")
        compressed_payload = zlib.compress(json_bytes, level=9)
        
        vec_array = np.array(vector, dtype=np.float32)
        vector_bytes = vec_array.tobytes()

        header = struct.pack(
            ">4sHH", 
            self.MAGIC_HEADER, 
            self.VERSION, 
            len(compressed_payload)
        )
        rmns_binary = header + compressed_payload + vector_bytes

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO lser_vectors (key, compressed_payload, vector_blob) VALUES (?, ?, ?)",
                (key, compressed_payload, vector_bytes)
            )
            conn.commit()

        return rmns_binary

    def unpack_state(self, rmns_binary: bytes) -> tuple[dict, np.ndarray]:
        """
        Unpacks and de-quantizes .rmns binary state locally.
        """
        header_size = struct.calcsize(">4sHH")
        magic, version, payload_len = struct.unpack(">4sHH", rmns_binary[:header_size])

        if magic != self.MAGIC_HEADER:
            raise ValueError("Invalid state format: Missing RMNS signature.")

        compressed_payload = rmns_binary[header_size:header_size + payload_len]
        vector_bytes = rmrs_bytes = rmns_binary[header_size + payload_len:]

        payload = json.loads(zlib.decompress(compressed_payload).decode("utf-8"))
        vector = np.frombuffer(vector_bytes, dtype=np.float32)

        return payload, vector
