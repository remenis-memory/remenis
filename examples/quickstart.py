import os
from remenis import MemoryEngine

def main():
    # 1. Initialize engine with a 10 MB local storage cap
    db_path = "./demo_agent_memory.db"
    engine = MemoryEngine(storage_path=db_path, max_memory_mb=10)
    print("MemoryEngine initialized.")

    # 2. Store sample agent interactions
    print("\nStoring memories...")
    engine.store("User prefers dark mode across all interfaces.", importance=1.5)
    engine.store("User is building an open-source AI project named Remenis.", importance=2.0)
    engine.store("User mentioned their favorite drink is unsweetened tea.", importance=1.0)
    print("Memories stored successfully.")

    # 3. Query relevant context
    query = "AI project"
    print(f"\nRecalling memories for query: '{query}'...")
    results = engine.recall(query, limit=2)

    for item in results:
        print(f" - [{item['score']}] {item['content']}")

    # Clean up demo database file
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    main()
