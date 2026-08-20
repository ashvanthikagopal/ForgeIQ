from __future__ import annotations

import json
import os
from typing import Any


class GeminiClient:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set."
            )

        from google import genai

        self.client = genai.Client(
            api_key=self.api_key
        )

        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:

        from google.genai import types

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,
                response_mime_type="application/json",
            ),
        )

        text = response.text

        return json.loads(text)