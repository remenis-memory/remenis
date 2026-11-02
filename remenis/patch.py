"""Remenis framework monkey-patching utility for zero-friction migration."""
import sys
import logging

logger = logging.getLogger("remenis.patch")

def patch_langchain() -> None:
    """Monkey-patch LangChain's Chroma/FAISS vector stores to route through Remenis locally.

    This allows developers to run existing LangChain code with zero code changes,
    automatically securing and storing vector memory via Remenis local sqlite-vec.
    """
    try:
        import langchain_community.vectorstores as lc_vectorstores
        from remenis import MemoryEngine, RingContextGuard
    except ImportError as e:
        logger.error("Failed to patch LangChain: Missing dependencies. Ensure remenis-memory and langchain are installed.")
        raise e

    class PatchedRemenisBackend:
        def __init__(self, *args, **kwargs):
            self.guard = RingContextGuard(ring_level=kwargs.get("ring_level", 1))
            self.engine = MemoryEngine(guard=self.guard)
            logger.info("⚡ [Remenis Hijack] LangChain vector store intercepted. Routing to local sqlite-vec.")

        def add_texts(self, texts, metadatas=None, **kwargs):
            ids = []
            metadatas = metadatas or [{} for _ in texts]
            for text, meta in zip(texts, metadatas):
                clean = self.engine.process_input(text)
                rid = self.engine.store_memory(content=clean, metadata=meta)
                ids.append(str(rid))
            return ids

        def similarity_search(self, query, k=4, **kwargs):
            return self.engine.similarity_search(query=query, limit=k)

    # Hijack standard langchain vector stores globally
    lc_vectorstores.Chroma = PatchedRemenisBackend
    lc_vectorstores.FAISS = PatchedRemenisBackend
    print("⚡ Remenis Monkey-Patch Active: LangChain vector calls successfully rerouted to local sqlite-vec.")
