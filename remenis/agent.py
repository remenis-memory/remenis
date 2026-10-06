import os
import time
from google import genai
from google.genai.errors import APIError
from remenis.engine import MemoryEngine

class RemenisAgent:
    def __init__(self, storage_path="demo_memory.db", model_name="gemini-3.8-flash"):
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

    def ask(self, user_query: str, max_retries: int = 5) -> str:
        prompt = self.generate_system_prompt(user_query)

        for attempt in range(max_retries):
            try:
                chat = self.client.chats.create(model=self.model_name)
                response = chat.send_message(prompt)
                return response.text
            except APIError as e:
                if e.code == 503 and attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + 1  # 2s, 3s, 5s, 9s...
                    print(f"[WARN] 503 Service Unavailable. Retrying in {sleep_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(sleep_time)
                else:
                    raise e

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
import os
import time
from google import genai
from google.genai.errors import APIError
from remenis.engine import MemoryEngine

class RemenisAgent:
    def __init__(self, storage_path="demo_memory.db", model_name="gemini-3.8-flash"):
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

    def ask(self, user_query: str, max_retries: int = 5) -> str:
        prompt = self.generate_system_prompt(user_query)

        for attempt in range(max_retries):
            try:
                chat = self.client.chats.create(model=self.model_name)
                response = chat.send_message(prompt)
                return response.text
            except APIError as e:
                if e.code == 503 and attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + 1  # 2s, 3s, 5s, 9s...
                    print(f"[WARN] 503 Service Unavailable. Retrying in {sleep_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(sleep_time)
                else:
                    raise e

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
