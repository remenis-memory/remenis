import time
import concurrent.futures
from remenis.engine import RemenisEngine

def benchmark_throughput():
    engine = RemenisEngine()
    engine.checkpoint_state("BENCH_START")
    
    total_ops = 5000
    start_time = time.time()

    def worker(i):
        engine.commit_memory(f"Benchmark payload item {i}", task_intent="benchmark", origin_type="tool_output")

    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        list(executor.map(worker, range(total_ops)))

    duration = time.time() - start_time
    ops_per_sec = total_ops / duration
    print(f"\n⚡ THROUGHPUT BENCHMARK: {ops_per_sec:.2f} ops/sec ({total_ops} ops in {duration:.3f}s)")

if __name__ == "__main__":
    benchmark_throughput()
