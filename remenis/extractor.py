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

    def _call_gemini_with_retry(self, prompt: str) -> str:
        for attempt in range(3):
            try:
                time.sleep(0.5)
                response = self.client.models.generate_content(
                    model='gemini-3-flash-preview',
                    contents=prompt,
                )
                return response.text
            except APIError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    time.sleep(5)
                else:
                    raise e
        return ""

    def extract_facts(self, text: str) -> list[str]:
        prompt = f"""
        You are an atomic fact extraction engine.
        Convert the input text into a list of concise, standalone factual statements.

        Rules:
        1. STRIP ALL FILLER: Remove conversational fluff, intros, transitions, and qualifiers (e.g., "Honestly", "To be frank", "So listen", "You know what").
        2. PRESERVE CONTEXT: Retain time, location, conditions, frequency, and situational constraints (e.g., "in the morning", "on rainy days", "when living in London").
        3. ATOMICITY: Each fact must stand on its own as a single clear truth.

        User input: "{text}"

        Return ONLY a JSON array of strings. Example: ["User drinks coffee in the morning.", "User drinks tea at night."]
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

    def resolve_conflicts_batch(self, new_facts: list[str], existing_memories: list) -> list[str]:
        if not existing_memories or not new_facts:
            return []

        formatted_memories = [
            {
                "id": str(m.get("id") if isinstance(m, dict) else getattr(m, "id", "")),
                "content": m.get("content") if isinstance(m, dict) else getattr(m, "content", "")
            }
            for m in existing_memories
        ]

        prompt = f"""
        Analyze whether any NEW FACTS render any EXISTING MEMORIES obsolete or invalid.

        Decision Rules:
        1. CONTEXTUAL CO-EXISTENCE: If two habits occur under DIFFERENT conditions (e.g., morning vs night, rainy days vs sunny days, home vs work), KEEP BOTH. They are NOT in conflict.
        2. DIRECT SUPERSEDENCE: If a new fact explicitly contradicts or replaces an existing memory without situational distinction (e.g., "User dropped Project X" vs "User works on Project X", or "User no longer drinks coffee" vs "User drinks coffee"), MARK THE OLD MEMORY FOR DELETION.
        3. EXPLICIT CLARIFICATION: If a new fact refines or corrects a general state (e.g., "User prefers turmeric tea over coffee" replacing a generic "User prefers coffee"), MARK THE OLD MEMORY FOR DELETION.

        NEW FACTS: {json.dumps(new_facts)}
        EXISTING MEMORIES: {json.dumps(formatted_memories)}

        Return ONLY a JSON array containing the string IDs of existing memories that MUST be deleted. Example: ["9"]
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
