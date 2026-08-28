from fastapi import FastAPI
from pydantic import BaseModel
from remenis.engine import MemoryEngine
from remenis.agent import RemenisAgent

app = FastAPI(title="Remenis Active Memory Engine")
engine = MemoryEngine(storage_path="demo_memory.db")
agent = RemenisAgent(storage_path="demo_memory.db")

class QueryRequest(BaseModel):
    query: str

class StoreRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "online", "system": "Remenis Active Memory Engine"}

@app.post("/store")
def store_memory(req: StoreRequest):
    engine.add_memory(req.text)
    return {"status": "success", "message": "Memory processed and stored."}

@app.post("/ask")
def ask_agent(req: QueryRequest):
    response = agent.ask(req.query)
    return {"query": req.query, "response": response}
