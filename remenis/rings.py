import hashlib

class PermissionDeniedError(Exception):
    """Raised when an agent attempts to access a memory ring above its clearance level."""
    pass

class RingIsolationEngine:
    # Ring 0 = Core/Kernel, Ring 1 = Shared/App, Ring 2 = Public/Temporary
    RING_LEVELS = {
        "kernel": 0,
        "core": 0,
        "system": 0,
        "user_preference": 1,
        "project_context": 1,
        "task_state": 2,
        "general": 2
    }

    def __init__(self):
        pass

    def get_category_ring(self, category: str) -> int:
        return self.RING_LEVELS.get(category.lower(), 2)

    def authorize_access(self, agent_ring: int, target_category: str) -> bool:
        """
        Enforces ring hierarchy: Agent Ring Level must be <= Target Category Ring Level.
        (e.g., Ring 1 Agent cannot access Ring 0 Kernel Memories).
        """
        target_ring = self.get_category_ring(target_category)
        if agent_ring > target_ring:
            raise PermissionDeniedError(
                f"⛔ [RING VIOLATION] Agent operating at Ring {agent_ring} "
                f"cannot access Ring {target_ring} memory category ('{target_category}')."
            )
        return True

if __name__ == "__main__":
    engine = RingIsolationEngine()
    print("Ring Isolation Engine ready.")
