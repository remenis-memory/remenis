from typing import Any, Dict, List
import logging
from remenis.engine import RemenisEngine
from remenis.sentinel import RemenisSentinel

logger = logging.getLogger(__name__)

class RemenisCrewStorage:
    """CrewAI storage and memory provider backed by Remenis embedded sqlite-vec."""

    def __init__(self, db_path: str = "agent_governance.db", enforce_policy: bool = True):
        self.engine = RemenisEngine(db_path=db_path)
        self.sentinel = RemenisSentinel()
        self.enforce_policy = enforce_policy

    def save(self, item: str, metadata: Dict[str, Any] = None) -> None:
        if self.enforce_policy and hasattr(self.sentinel, "detect_rogue_behavior") and self.sentinel.detect_rogue_behavior(item, ""):
            logger.warning("[Remenis Governance] Blocked CrewAI task output due to security policy.")
            return
        self.engine.remember(item)

    def search(self, query: str, limit: int = 3) -> List[str]:
        raw_memories = self.engine.recall(query)
        if isinstance(raw_memories, list):
            return raw_memories[:limit]
        return [str(raw_memories)]
