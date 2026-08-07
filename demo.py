import time
from remenis.engine import MemoryEngine

def run_demo():
    print("=" * 50)
    print("      REMENIS END-TO-END SYSTEM DEMO")
    print("=" * 50)

    # Initialize engine with a clean demo database
    engine = MemoryEngine(storage_path="./demo_memory.db")

    print("\n1. Testing Fact Extraction & Clean Storage")
    print("-" * 50)

    # Raw conversational inputs
    raw_input_1 = "Um, I think I love building AI agents on my Chromebook. Please note that I prefer pure turmeric tea."
    print(f"Storing Raw Input: '{raw_input_1}'")
    
    ids = engine.store(raw_input_1, importance=1.5)
    print(f"Extracted and saved as Memory IDs: {ids}")

    print("\n2. Testing Recall & Mathematical Scoring")
    print("-" * 50)

    query = "What do I like to drink?"
    print(f"Querying: '{query}'")
    results = engine.recall(query, top_k=2)

    for res in results:
        print(f" -> [ID {res['id']}] Content: '{res['content']}'")
        print(f"    Similarity: {res['similarity']} | Final Score: {res['final_score']}")

    print("\n3. Testing Conflict Resolution & Memory Overwrite")
    print("-" * 50)

    # New contradictory memory
    conflict_input = "Actually, I prefer coffee instead of turmeric tea."
    print(f"Storing Updated Preference: '{conflict_input}'")
    
    new_ids = engine.store(conflict_input, importance=2.0)
    print(f"Saved new Memory ID: {new_ids}")

    print(f"\nRe-querying: '{query}' after preference update...")
    updated_results = engine.recall(query, top_k=2)

    for res in updated_results:
        print(f" -> [ID {res['id']}] Content: '{res['content']}'")
        print(f"    Similarity: {res['similarity']} | Final Score: {res['final_score']}")

    print("\n=" * 50)
    print("      DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)

if __name__ == "__main__":
    run_demo()

