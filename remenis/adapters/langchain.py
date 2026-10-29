from typing import Any, Dict, List
import logging
from remenis.engine import RemenisEngine
from remenis.sentinel import RemenisSentinel

logger = logging.getLogger(__name__)

class RemenisGovernanceMemory:
    """LangChain memory provider backed by Remenis embedded sqlite-vec storage."""

    def __init__(self, db_path: str = "agent_governance.db", enforce_policy: bool = True):
        self.engine = RemenisEngine(db_path=db_path)
        self.sentinel = RemenisSentinel()
        self.enforce_policy = enforce_policy

    @property
    def memory_variables(self) -> List[str]:
        return ["history"]

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        user_input = inputs.get("input") or inputs.get("human_input", "")
        agent_output = outputs.get("output") or outputs.get("response", "")

        if self.enforce_policy and hasattr(self.sentinel, "detect_rogue_behavior") and self.sentinel.detect_rogue_behavior(user_input, agent_output):
            logger.warning("[Remenis Governance] Blocked attempt at unauthorized state persistence.")
            return

        if user_input:
            self.engine.remember(f"User: {user_input}")
        if agent_output:
            self.engine.remember(f"Agent: {agent_output}")

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("input") or inputs.get("human_input", "")
        if not query:
            return {"history": ""}

        raw_memories = self.engine.recall(query)
        sanitized = self.sentinel.sanitize_context(raw_memories) if self.enforce_policy and hasattr(self.sentinel, "sanitize_context") else raw_memories
        formatted = "\n".join(sanitized) if isinstance(sanitized, list) else str(sanitized)
        return {"history": formatted}
