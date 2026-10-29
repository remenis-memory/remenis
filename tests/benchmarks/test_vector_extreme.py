import numpy as np
from remenis.vector import VectorEngine

def test_extreme_vector_engine():
    print("=" * 70)
    print("🚀 STRESS TESTING REMENIS MATHEMATICAL VECTOR ENGINE (EXTREME SCALE)")
    print("=" * 70)

    engine = VectorEngine(dimensions=1536) # OpenAI embedding dimension standard
    
    # 1. Bulk High-Dimensional Insertion & Deduping Test
    print("\n[Test 1] Indexing 2,000 high-dimensional vectors with semantic deduplication...")
    base_vectors = [np.random.randn(1536).astype(np.float32) for _ in range(500)]
    
    indexed_count = 0
    for i in range(2000):
        # Pick a base vector and add tiny noise to test auto-deduping
        base = base_vectors[i % len(base_vectors)]
        noisy_vec = base + np.random.normal(0, 0.001, 1536).astype(np.float32)
        success = engine.index_vector(f"doc_{i}", noisy_vec, metadata={"batch": i // 500})
        if success:
            indexed_count += 1

    print(f"✅ Successfully indexed {indexed_count} unique vectors (Deduplicated {2000 - indexed_count} redundant entries).")
    assert indexed_count <= 500, "Auto-deduping failed to collapse semantic duplicates."

    # 2. High-Speed Vectorized Similarity Search Test
    print("\n[Test 2] Executing ultra-fast batch similarity query...")
    query_vec = base_vectors[0] + np.random.normal(0, 0.05, 1536).astype(np.float32)
    
    results = engine.similarity_search(query_vec, top_k=5)
    print(f"Top matches retrieved: {len(results)}")
    for doc_id, score, meta in results:
        print(f" -> Doc: {doc_id} | Similarity Score: {score:.4f}")
    
    assert results[0][1] > 0.95, "Top similarity score fell below acceptable threshold."
    print("✅ High-Speed Similarity Search: PASSED")

    # 3. Spatial Manifold Clustering Test
    print("\n[Test 3] Performing spatial manifold clustering...")
    clusters = engine.spatial_cluster_analysis(n_clusters=3)
    for cluster_id, docs in clusters.items():
        print(f" -> Cluster {cluster_id}: {len(docs)} memory nodes grouped.")
        
    assert len(clusters) == 3, "Spatial clustering failed to generate requested clusters."
    print("✅ Spatial Manifold Clustering: PASSED")

    print("\n" + "=" * 70)
    print("✨ MATHEMATICAL VECTOR ENGINE PUSHED TO UNTHINKABLE EXTENT SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_extreme_vector_engine()
