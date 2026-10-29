import argparse
import sys
from .engine import RemenisEngine

def main():
    parser = argparse.ArgumentParser(description="Remenis: Enterprise AI Memory Middleware CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'commit' subcommand
    commit_parser = subparsers.add_parser("commit", help="Commit a secure memory frame")
    commit_parser.add_argument("content", type=str, help="Content payload to commit")
    commit_parser.add_argument("--intent", type=str, default="default_task", help="Task intent")
    commit_parser.add_argument("--origin", type=str, default="cli", help="Origin type")
    commit_parser.add_argument("--vector", type=float, nargs='+', default=[1.0, 0.0, 0.0], help="Embedding vector floats")

    # 'audit' subcommand
    subparsers.add_parser("audit", help="View provenance audit log")

    # 'status' subcommand
    subparsers.add_parser("status", help="View active middleware metrics and vector counts")

    args = parser.parse_args()
    engine = RemenisEngine(vector_dimension=3)

    if args.command == "commit":
        success, result = engine.commit_memory(
            content=args.content,
            task_intent=args.intent,
            vector=args.vector,
            origin_type=args.origin
        )
        if success:
            print(f"SUCCESS: Committed memory frame -> ID: {result}")
        else:
            print(f"REJECTED: {result}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "audit":
        log = engine.get_audit_log()
        print(f"--- Remenis Provenance Audit Log ({len(log)} frames) ---")
        for frame in log:
            print(f"[{frame['timestamp']}] ID: {frame['frame_id']} | Intent: {frame['task_intent']} | Content: {frame['content']}")

    elif args.command == "status":
        status = engine.get_status()
        print("=== Remenis Middleware Status ===")
        print(f"Database Path       : {status['db_path']}")
        print(f"Indexed Vectors     : {status['vector_count']}")
        print(f"Audit Log Frames    : {status['audit_log_size']}")
        print(f"Active State Items  : {status['active_state_size']}")

if __name__ == "__main__":
    main()
