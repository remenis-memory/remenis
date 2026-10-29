import time
from remenis.archive import ArchiveManager

def test_extreme_archive_engine():
    print("=" * 70)
    print("🚀 STRESS TESTING REMENIS ARCHIVE MANAGER (EXTREME SCALE)")
    print("=" * 70)

    manager = ArchiveManager(namespace="enterprise_core")

    # 1. High-Volume Snapshot Ingestion Test
    print("\n[Test 1] Committing 500 temporal archive snapshots...")
    base_time = time.time() - 86400 * 10
    for i in range(500):
        is_anchor = (i % 50 == 0) # Mark every 50th record as a critical anchor
        manager.commit_snapshot(
            content=f"Agent telemetry state snapshot record #{i}",
            timestamp=base_time + (i * 3600),
            metadata={"anchor": is_anchor}
        )
    
    print(f"✅ Total snapshots committed: {len(manager.fetch_active_archives())}")
    assert len(manager.fetch_active_archives()) == 500

    # 2. Temporal Branching & Sandboxing Test
    print("\n[Test 2] Forking temporal branches for autonomous agent simulation...")
    manager.create_branch("agent_experiment_sandbox")
    manager.switch_branch("agent_experiment_sandbox")
    
    manager.commit_snapshot("Sandbox isolated mutation record", timestamp=time.time(), metadata={"anchor": True})
    print(f"Active branch '{manager.active_branch}' snapshots: {len(manager.fetch_active_archives())}")
    assert len(manager.fetch_active_archives()) == 501

    # Switch back to main branch to verify isolation
    manager.switch_branch("main")
    print(f"Active branch '{manager.active_branch}' snapshots: {len(manager.fetch_active_archives())}")
    assert len(manager.fetch_active_archives()) == 500
    print("✅ Temporal Branching & Sandboxing: PASSED")

    # 3. Snapshot Compaction & Bloat Pruning Test
    print("\n[Test 3] Executing hierarchical snapshot compaction...")
    manager.switch_branch("agent_experiment_sandbox")
    pruned = manager.compact_historical_snapshots(retention_limit=50)
    print(f"Pruned {pruned} legacy snapshots, retained {len(manager.fetch_active_archives())} critical nodes.")
    
    assert len(manager.fetch_active_archives()) <= 60, "Snapshot compaction failed to prune bloat effectively."
    print("✅ Hierarchical Snapshot Compaction: PASSED")

    print("\n" + "=" * 70)
    print("✨ ARCHIVE MANAGER PUSHED TO UNTHINKABLE EXTENT SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_extreme_archive_engine()
