def patch_langchain():
    """Overrides default LangChain memory buffers with Remenis local security proxy."""
    try:
        import langchain.memory
        from remenis.adapters.langchain import RemenisGovernanceMemory
        
        langchain.memory.VectorStoreRetrieverMemory = RemenisGovernanceMemory
        langchain.memory.ConversationBufferMemory = RemenisGovernanceMemory
        print("[remenis] LangChain memory patched successfully.")
    except ImportError:
        pass

def patch_all():
    patch_langchain()
