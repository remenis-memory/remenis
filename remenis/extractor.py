import os
import json
from google import genai

class FactExtractor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        self.client = genai.Client(api_key=api_key)

    def extract_facts(self, text: str) -> list[str]:
        prompt = f"""
        Extract concise, standalone atomic facts from the following user input.
        Remove filler words, conversational headers (e.g., 'Um', 'Please note that'), and fluff.
        Preserve contextual nuances (such as time, situation, or conditions).
        Return ONLY a JSON array of strings containing the facts.

        User input: "{text}"
        """

        response = self.client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
        )

        try:
            cleaned_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
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
        If the new fact updates or replaces an existing memory (e.g. changed drink preference), identify its ID.

        New fact: "{new_fact}"
        Existing memories: {json.dumps(formatted_memories)}

        Return ONLY a JSON array of string IDs to delete/supersede. Example: ["5"]
        """

        response = self.client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
        )

        try:
            cleaned_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            conflicts = json.loads(cleaned_text)
            if isinstance(conflicts, list):
                return [str(cid) for cid in conflicts]
        except Exception:
            pass

        return []
