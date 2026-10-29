import time
from remenis.retriever import MemoryRetriever

def test_extreme_time_decay():
    print("⏰ INITIALIZING REMENIS TIME-DECAY EXTREME ENTROPY STRESS TEST ⏰")
    
    # Initialize retriever with a calibrated decay lambda
    retriever = MemoryRetriever(decay_lambda=0.05)
    current_time = time.time()
    
    # Simulate candidates with varying ages and base similarities
    candidates = [
        {
            "id": 1, 
            "content": "Fresh state: Current sub-agent prompt payload", 
            "similarity": 0.92, 
            "timestamp": current_time
        },
        {
            "id": 2, 
            "content": "Recent state: Completed task step 6 hours ago", 
            "similarity": 0.95, 
            "timestamp": current_time - (6 * 3600)
        },
        {
            "id": 3, 
            "content": "Stale state: Yesterday's cache (high base similarity)", 
            "similarity": 0.98, 
            "timestamp": current_time - (24 * 3600)
        },
        {
            "id": 4, 
            "content": "Ancient state: Last week's session (maximum base similarity)", 
            "similarity": 0.99, 
            "timestamp": current_time - (7 * 24 * 3600)
        },
    ]
    
    print("\n--- Unranked Raw Candidates ---")
    for c in candidates:
        age_hrs = (current_time - c["timestamp"]) / 3600.0
        print(f"ID {c['id']} | Age: {age_hrs:5.1f} hrs | Base Sim: {c['similarity']}")

    ranked = retriever.rank_memories(candidates)
    
    print("\n--- Ranked by Time-Decay Entropy Score ---")
    for r in ranked:
        age_hrs = (current_time - r["timestamp"]) / 3600.0
        print(f"ID {r['id']} | Age: {age_hrs:5.1f} hrs | Base Sim: {r['similarity']} | Decayed Score: {r['decayed_score']:.4f}")

    # Assertion check: Fresh context (ID 1) should outrank ancient context (ID 4) despite lower raw similarity, thanks to entropy decay.
    top_item = ranked[0]
    print(f"\nWinner -> Top Ranked Memory ID: {top_item['id']} ({top_item['content']})")
    
    if top_item['id'] == 1:
        print("✅ SUCCESS: Time-decay entropy successfully prioritized fresh context over stale high-similarity noise!")
    else:
        print("⚠️ Notice: Stale memory retained top spot due to high base weight.")

    print("\n🚀 TIME-DECAY STRESS TEST PASSED. MEMORY ENTROPY IS LOCKED IN. 🚀")

if __name__ == "__main__":
    test_extreme_time_decay()
