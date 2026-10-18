import concurrent.futures
from remenis.engine import RemenisEngine

def test_concurrent_sentinel_writes():
    engine = RemenisEngine()
    engine.checkpoint_state("BASE_SNAPSHOT")

    def worker(task_id: int):
        intent = f"task_{task_id % 3}"
        content = f"Data payload {task_id} processed successfully."
        success, _ = engine.commit_memory(content, task_intent=intent, origin_type="tool_output")
        return success

    # Run 32 concurrent worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(worker, i) for i in range(100)]
        results = [f.result() for f in futures]

    assert all(results), "Some concurrent memory commits failed validation!"
    audit_log = engine.get_audit_log()
    print(f"\n🚀 MULTI-THREADED STRESS BENCHMARK PASSED: {len(audit_log)} secure frames committed concurrently.")

if __name__ == "__main__":
    test_concurrent_sentinel_writes()
