from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from remenis.adapters import RemenisLangChainVectorStore
from remenis import RemenisCore

# 1. Initialize local hyper-dense binary storage (.rmns)
core = RemenisCore(db_path="langchain_state.rmns")

# 2. Wrap into LangChain vector store middleware (91% token reduction)
vectorstore = RemenisLangChainVectorStore(core_engine=core)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

print("[SUCCESS] Remenis binary memory successfully bound to LangChain retriever.")
