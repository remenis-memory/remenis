from remenis.vector_store import VectorStore

def test_vector_deduplication():
    store = VectorStore(dimension=3)
    
    # 1. Add initial vector
    vec_a = [1.0, 0.0, 0.0]
    success, reason = store.add_vector("frame_001", "Cargo cleared at port.", vec_a)
    assert success is True
    assert reason == "VECTOR_INDEXED"

    # 2. Try adding a near-identical duplicate vector
    vec_b = [0.99, 0.01, 0.0]
    success, reason = store.add_vector("frame_002", "Cargo cleared at port (duplicate).", vec_b, similarity_threshold=0.95)
    assert success is False
    assert "DUPLICATE_REJECTED" in reason

    # 3. Add a distinct vector
    vec_c = [0.0, 1.0, 0.0]
    success, reason = store.add_vector("frame_003", "Customs inspection pending.", vec_c)
    assert success is True
    assert reason == "VECTOR_INDEXED"

    print("\n✅ VECTOR DEDUPLICATION TEST PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_vector_deduplication()
