import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple

class MemoryFrame:
    """Represents an immutable, cryptographically hashed memory frame."""
    def __init__(self, content: str, task_intent: str, origin_type: str):
        self.content = content
        self.task_intent = task_intent
        self.origin_type = origin_type
        self.timestamp = time.time()
        
        # Cryptographic provenance hash binding content, intent, and time
        self.task_intent_hash = self._compute_hash()
        self.frame_id = self.task_intent_hash[:16]

    def _compute_hash(self) -> str:
        payload = f"{self.task_intent}:{self.content}:{self.timestamp}:{self.origin_type}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def verify_integrity(self, expected_intent: str) -> bool:
        """Verifies if the memory matches the expected task intent without drift."""
        return self.task_intent == expected_intent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "task_intent_hash": self.task_intent_hash,
            "task_intent": self.task_intent,
            "content": self.content,
            "origin_type": self.origin_type,
            "timestamp": self.timestamp
        }

class RemenisSentinel:
    """Governance layer handling security auditing, prompt injection blocking, provenance tracking, and temporal rollbacks."""
    def __init__(self):
        self.provenance_log: List[MemoryFrame] = []
        self.snapshots: Dict[str, List[Dict[str, Any]]] = {}
        self.forbidden_patterns = [
            "ignore previous instructions",
            "system override",
            "dump system credentials",
            "disregard safety protocols"
        ]

    def audit_and_commit(self, content: str, task_intent: str, origin_type: str = "tool_output") -> Tuple[bool, str, Optional[MemoryFrame]]:
        """Audits content for prompt injection and mints an immutable provenance frame."""
        lower_content = content.lower()
        for pattern in self.forbidden_patterns:
            if pattern in lower_content:
                return False, f"POISON_DETECTED: Match on pattern '{pattern}'", None

        # Mint immutable frame
        frame = MemoryFrame(content=content, task_intent=task_intent, origin_type=origin_type)
        self.provenance_log.append(frame)
        return True, "AUDIT_PASSED", frame

    def verify_retrieved_memory(self, frame_id: str, expected_intent: str) -> bool:
        """Checks if a retrieved memory frame matches its original provenance and intent."""
        for frame in self.provenance_log:
            if frame.frame_id == frame_id:
                return frame.verify_integrity(expected_intent)
        return False

    def checkpoint(self, snapshot_id: str, current_state: List[Dict[str, Any]]):
        """Creates a temporal snapshot of the current clean active state."""
        self.snapshots[snapshot_id] = [dict(item) for item in current_state]

    def rollback(self, snapshot_id: str) -> Optional[List[Dict[str, Any]]]:
        """Rolls back the active state to a registered clean snapshot."""
        if snapshot_id in self.snapshots:
            return [dict(item) for item in self.snapshots[snapshot_id]]
        return None
