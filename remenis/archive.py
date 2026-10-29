import time
import copy
from typing import List, Dict, Optional

class ArchiveManager:
    """
    Enterprise-Grade Archive Manager with Temporal Branching,
    Hierarchical Snapshot Compaction, and Namespace Isolation.
    """
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.archives: List[Dict] = []
        self.branches: Dict[str, List[Dict]] = {"main": []}
        self.active_branch: str = "main"

    def commit_snapshot(self, content: str, timestamp: float = None, metadata: dict = None) -> int:
        """Commits a structured memory snapshot to the active temporal branch."""
        snapshot = {
            "id": len(self.archives) + 1,
            "content": content,
            "timestamp": timestamp or time.time(),
            "metadata": metadata or {}
        }
        self.archives.append(snapshot)
        self.branches[self.active_branch].append(snapshot)
        return snapshot["id"]

    def create_branch(self, branch_name: str) -> bool:
        """Forks the current archive state into a new temporal branch for agent sandboxing."""
        if branch_name in self.branches:
            return False
        # Deep copy current branch state
        self.branches[branch_name] = copy.deepcopy(self.branches[self.active_branch])
        return True

    def switch_branch(self, branch_name: str) -> bool:
        """Switches the active operational context branch."""
        if branch_name not in self.branches:
            return False
        self.active_branch = branch_name
        return True

    def compact_historical_snapshots(self, retention_limit: int = 50) -> int:
        """
        Executes hierarchical snapshot compaction, pruning historical bloat
        while preserving high-weight critical anchor records.
        """
        current_branch_archives = self.branches[self.active_branch]
        initial_count = len(current_branch_archives)
        
        if initial_count > retention_limit:
            # Retain recent records and anchor nodes (e.g., tagged important)
            recent = current_branch_archives[-retention_limit:]
            anchors = [a for a in current_branch_archives[:-retention_limit] if a.get("metadata", {}).get("anchor", False)]
            
            # Recombine and sort chronologically
            compacted = sorted(anchors + recent, key=lambda x: x["timestamp"])
            self.branches[self.active_branch] = compacted
            
            pruned_count = initial_count - len(compacted)
            return pruned_count
        return 0

    def fetch_active_archives(self) -> List[Dict]:
        """Retrieves all memory snapshots for the currently active temporal branch."""
        return self.branches[self.active_branch]
