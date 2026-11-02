from semantic_kernel.kernel_pydantic import KernelPydantic
from remenis import RemenisCore

class RemenisMemoryPlugin(KernelPydantic):
    def __init__(self, db_path="remenis.db"):
        super().__init__()
        self.engine = RemenisCore(db_path=db_path)

    def save_memory(self, collection: str, key: str, text: str):
        self.engine.store_plugin_memory(collection=collection, key=key, value=text)

    def recall_memory(self, collection: str, query: str):
        return self.engine.recall_plugin_memory(collection=collection, query=query)
