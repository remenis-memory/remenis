from remenis import RemenisCore

class RemenisAutoGenContextManager:
    def __init__(self, db_path="remenis.db"):
        self.engine = RemenisCore(db_path=db_path)

    def register_message(self, sender: str, recipient: str, message: str):
        self.engine.log_interaction(sender=sender, recipient=recipient, content=message)

    def get_context_window(self, agent_id: str, max_tokens: int = 1000):
        return self.engine.get_compressed_history(identifier=agent_id, token_limit=max_tokens)
