import argparse
from .engine import RemenisEngine
from .synthesizer import MemorySynthesizer
from .rings import RingIsolationEngine, PermissionDeniedError

def run_pipeline():
    parser = argparse.ArgumentParser(description="Remenis AI Memory Middleware CLI")
    parser.add_argument("--add", type=str, help="Add a new raw text observation to memory")
    parser.add_argument("--category", type=str, default="general", help="Category for the memory")
    parser.add_argument("--query", type=str, help="Search memory using vector similarity")
    parser.add_argument("--audit", action="store_true", help="Print trace audit report")
    parser.add_argument("--synthesize", action="store_true", help="Run memory synthesis pipeline")
    parser.add_argument("--agent-ring", type=int, default=0, help="Ring isolation level (0-3)")

    args = parser.parse_args()

    engine = RemenisEngine()
    ring_engine = RingIsolationEngine()

    if args.add:
        try:
            ring_engine.authorize_access(args.agent_ring, args.category)
            engine.store_memory(args.add, category=args.category)
        except PermissionDeniedError as e:
            print(e)

    if args.synthesize:
        synthesizer = MemorySynthesizer(engine.conn)
        synthesizer.consolidate_duplicates()

    if args.query:
        try:
            ring_engine.authorize_access(args.agent_ring, args.category)
            print(f"🔎 [QUERY | Ring {args.agent_ring}]: Searching category '{args.category}'...")
            cursor = engine.conn.cursor()
            cursor.execute("SELECT id, fact_text, category, importance FROM memories WHERE category = ?", (args.category,))
            results = cursor.fetchall()
            if results:
                for r in results:
                    print(f"  └─ [ID {r[0]}] (Imp: {r[3]}) {r[1]}")
            else:
                print("  └─ No matching memories found.")
        except PermissionDeniedError as e:
            print(e)

    if args.audit:
        engine.audit_inspect()

if __name__ == "__main__":
    run_pipeline()
