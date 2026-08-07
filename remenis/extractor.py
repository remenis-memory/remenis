import os
import json
import time
from google import genai
from google.genai.errors import APIError

class FactExtractor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        self.client = genai.Client(api_key=api_key)

    def _call_gemini_with_retry(self, prompt: str):
        """Helper to call Gemini API with rate-limit retry logic."""
        for attempt in range(3):
            try:
                time.sleep(1)  # Brief pause to respect 5 RPM limit
                response = self.client.models.generate_content(
                    model='gemini-3-flash-preview',
                    contents=prompt,
                )
                return response.text
            except APIError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    time.sleep(15)  # Wait for quota window to clear
                else:
                    raise e
        return ""

    def extract_facts(self, text: str) -> list[str]:
        prompt = f"""
        Extract concise, standalone atomic facts from the following user input.
        Remove filler words, conversational headers, and fluff.
        Preserve contextual nuances (time, situation, past vs present, conditions).
        Return ONLY a JSON array of strings containing the facts.

        User input: "{text}"
        """

        raw_text = self._call_gemini_with_retry(prompt)

        try:
            cleaned_text = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
            facts = json.loads(cleaned_text)
            if isinstance(facts, list):
                return facts
        except Exception:
            pass

        return [text]

    def resolve_conflicts(self, new_fact: str, existing_memories: list) -> list[str]:
        if not existing_memories:
            return []

        formatted_memories = [
            {
                "id": str(getattr(m, "id", m.get("id") if isinstance(m, dict) else "")),
                "content": getattr(m, "content", m.get("content") if isinstance(m, dict) else "")
            }
            for m in existing_memories
        ]

        prompt = f"""
        Analyze if the new fact directly contradicts or updates any existing memories.
        If the new fact explicitly updates or replaces an existing memory (e.g. dropped project, changed location, updated drink), identify its ID.
        If it is a conditional exception (e.g. turmeric tea on rainy Sundays vs iced matcha daily), it is NOT a contradiction.

        New fact: "{new_fact}"
        Existing memories: {json.dumps(formatted_memories)}

        Return ONLY a JSON array of string IDs to delete/supersede. Example: ["5"]
        """

        raw_text = self._call_gemini_with_retry(prompt)

        try:
            cleaned_text = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
            conflicts = json.loads(cleaned_text)
            if isinstance(conflicts, list):
                return [str(cid) for cid in conflicts]
        except Exception:
            pass

        return []
