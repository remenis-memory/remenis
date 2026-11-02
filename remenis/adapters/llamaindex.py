from remenis import RemenisCore
from llama_index.core.vector_stores.types import BasePydanticVectorStore

class RemenisLlamaIndexWrapper(BasePydanticVectorStore):
    store_type: str = "remenis_vector"

    def __init__(self, db_path="remenis.db"):
        super().__init__()
        self.engine = RemenisCore(db_path=db_path)

    def add(self, nodes, **kwargs) -> list[str]:
        for node in nodes:
            self.engine.index_document(node_id=node.node_id, text=node.text, embedding=node.embedding)
        return [node.node_id for node in nodes]

    def query(self, query_embed: list[float], similarity_top_k: int = 4):
        return self.engine.similarity_search(embedding=query_embed, top_k=similarity_top_k)
