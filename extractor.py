import time
from google import genai
from google.genai.errors import APIError

class FactExtractor:
    def __init__(self, model_name="gemini-3.8-flash"):
        self.model_name = model_name
        self.client = genai.Client()

    def _call_gemini_with_retry(self, prompt: str, max_retries: int = 5) -> str:
        for attempt in range(max_retries):
            try:
                chat = self.client.chats.create(model=self.model_name)
                response = chat.send_message(prompt)
                return response.text
            except APIError as e:
                if e.code == 503 and attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + 1
                    time.sleep(sleep_time)
                else:
                    raise e
        return ""

    def extract_facts(self, text: str) -> list[str]:
        prompt = f"""Extract concise, atomic factual statements from the following text as a bulleted list. Return only the facts.
Text: "{text}"
Facts:"""
        try:
            raw_text = self._call_gemini_with_retry(prompt)
            lines = [line.strip("- *").strip() for line in raw_text.split("\n") if line.strip()]
            return [l for l in lines if l]
        except Exception:
            return [text]
import time
from google import genai
from google.genai.errors import APIError

class FactExtractor:
    def __init__(self, model_name="gemini-3.8-flash"):
        self.model_name = model_name
        self.client = genai.Client()

    def _call_gemini_with_retry(self, prompt: str, max_retries: int = 5) -> str:
        for attempt in range(max_retries):
            try:
                chat = self.client.chats.create(model=self.model_name)
                response = chat.send_message(prompt)
                return response.text
            except APIError as e:
                if e.code == 503 and attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + 1
                    time.sleep(sleep_time)
                else:
                    raise e
        return ""

    def extract_facts(self, text: str) -> list[str]:
        prompt = f"""Extract concise, atomic factual statements from the following text as a bulleted list. Return only the facts.
Text: "{text}"
Facts:"""
        try:
            raw_text = self._call_gemini_with_retry(prompt)
            lines = [line.strip("- *").strip() for line in raw_text.split("\n") if line.strip()]
            return [l for l in lines if l]
        except Exception:
            return [text]
