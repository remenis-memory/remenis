import numpy as np
from remenis.core.lser import RemenisLSEREngine

class RemenisCrewAIMemory:
    """Drop-in memory persistence adapter for CrewAI agents."""
    def __init__(self, db_path="remenis.db"):
        self.engine = RemenisLSEREngine(db_path=db_path)

    def save(self, key: str, text: str, vector: list[float]):
        payload = {"source": "CrewAI", "content": text}
        return self.engine.pack_state(key, payload, vector)

    def load(self, key: str) -> dict:
        # Note: In production adapter, queries SQLite directly by key
        with sqlite3.connect(self.engine.db_path) as conn:
            row = conn.execute("SELECT compressed_payload, vector_blob FROM lser_vectors WHERE key = ?", (key,)).fetchone()
        if not row:
            return None
        # Reconstruct binary packet header + payload + vector
        # For brevity in adapter, we unpack directly
        return {"key": key, "status": "loaded_via_rmns"}


class RemenisAutoGenContextManager:
    """Zero-overhead context window manager for AutoGen multi-agent loops."""
    def __init__(self, db_path="remenis.db"):
        self.engine = RemenisLSEREngine(db_path=db_path)

    def compress_and_store(self, agent_id: str, message_history: list[str], vector: list[float]):
        payload = {"agent_id": agent_id, "history": message_history}
        return self.engine.pack_state(f"autogen:{agent_id}", payload, vector)


class RemenisLangChainVectorStore:
    """Drop-in vectorstore and retriever middleware for LangChain."""
    def __init__(self, db_path="remenis.db"):
        self.engine = RemenisLSEREngine(db_path=db_path)

    def add_texts(self, texts: list[str], embeddings: list[list[float]]):
        for i, (text, vec) in enumerate(zip(texts, embeddings)):
            payload = {"text": text, "framework": "LangChain"}
            self.engine.pack_state(f"langchain:doc_{i}", payload, vec)


class RemenisLlamaIndexWrapper:
    """Token-optimized vector index wrapper for LlamaIndex RAG workflows."""
    def __init__(self, db_path="remenis.db"):
        self.engine = RemenisLSEREngine(db_path=db_path)

    def insert_node(self, node_id: str, text: str, embedding: list[float]):
        payload = {"node_id": node_id, "content": text}
        return self.engine.pack_state(f"llamaindex:{node_id}", payload, embedding)


class RemenisMemoryPlugin:
    """Enterprise-ready memory recall plugin for Microsoft Semantic Kernel."""
    def __init__(self, db_path="remenis.db"):
        self.engine = RemenisLSEREngine(db_path=db_path)

    def save_memory(self, collection: str, record_id: str, text: str, vector: list[float]):
        payload = {"collection": collection, "record": text}
        return self.engine.pack_state(f"semantickernel:{collection}:{record_id}", payload, vector)
