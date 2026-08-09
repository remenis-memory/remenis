import os
from google import genai
from remenis.engine import MemoryEngine

class RemenisAgent:
    def __init__(self, storage_path="demo_memory.db", model_name="gemini-3.5-flash"):
        self.engine = MemoryEngine(storage_path=storage_path)
        self.model_name = model_name
        self.client = genai.Client()

    def generate_system_prompt(self, user_query: str) -> str:
        memories = self.engine.query(user_query, top_k=3, include_archived=False)
        context_str = "\n".join([f"- {m['content']}" for m in memories]) if memories else "No relevant prior context."
        
        return f"""[RECOLLECTED CONTEXT]
{context_str}

[USER QUERY]
{user_query}"""

    def ask(self, user_query: str) -> str:
        prompt = self.generate_system_prompt(user_query)
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text

if __name__ == "__main__":
    agent = RemenisAgent()
    
    query = "What should I make to drink while I work tonight?"
    print(f"User Query: {query}\n")
    print("=== GEMINI RESPONSE ===")
    
    try:
        reply = agent.ask(query)
        print(reply)
    except Exception as e:
        print(f"API Error: {e}")
