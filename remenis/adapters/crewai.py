from remenis import RemenisCore

class RemenisCrewAIMemory:
    def __init__(self, db_path="remenis.db"):
        self.engine = RemenisCore(db_path=db_path)

    def save(self, value: str, agent_name: str, metadata: dict = None):
        compressed_context = self.engine.compress(value)
        self.engine.store(key=f"crewai:{agent_name}", value=compressed_context, metadata=metadata or {})

    def search(self, query: str, limit: int = 5):
        return self.engine.vector_search(query=query, limit=limit)
