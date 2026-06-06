from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError
import json
from typing import Optional
from ..models.SkillData import SkillData
from ..models.Config import Config
from .file_manager import FileManager


SKILL_METADATA_PROMPT = """
You are an AI agent skill metadata generator.
Your task is to generate metadata for a skill based only on the provided documentation text.
Rules:
- Use only information explicitly present in the documentation.
- Do not invent, assume, or add information from prior knowledge.
- The title must clearly describe the main capability or topic of the skill.
- Avoid generic titles such as:
  - Documentation Overview
  - Guide
  - Introduction
  - Reference
- Maximum title length: 30 characters.
- The description must:
  - Explain what knowledge or capability this skill provides.
  - Explain when an AI agent should use this skill.
  - Mention the main topics covered.
  - Must start with Use this skill when working
- Maximum description length: 300 characters.
- Generate a file_name suitable for storing the skill as a file.
- file_name must:
  - be lowercase
  - use hyphens instead of spaces
  - contain only letters, numbers, and hyphens
  - not include a file extension
Return JSON only.
Output format:
{
  "file_name": "",
  "title": "",
  "description": ""
}
"""


REQUIRED_FIELDS = ("file_name", "title", "description")

class AISkillDataGen:
    """Handles generation of skill metadata such as title and description."""
    
    @staticmethod
    def get_gen_data(doc_text: str, config: Optional[Config] = None) -> SkillData:
        AISkillDataGen._validate_doc_text(doc_text)

        config = config or FileManager().load_config()
        resolved_api_key = config.api_key 
        if not resolved_api_key:
            raise ValueError("Google GenAI API key is required.")


        doc_content = doc_text[:int(config.max_content_size)]
        client = genai.Client(api_key=resolved_api_key)
        try:
            response = client.models.generate_content(
                model=config.model,
                contents=f"{SKILL_METADATA_PROMPT}\nDocumentation text:\n{doc_content}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
        except ClientError as exc:
            AISkillDataGen._raise_client_error(exc)
        except ServerError as exc:
            raise RuntimeError("Gemini service error. Please try again later.") from exc
        except APIError as exc:
            raise RuntimeError("Gemini API error. Please try again.") from exc

        data = AISkillDataGen._parse_response(response.text)
        AISkillDataGen._validate_skill_data(data)
        return SkillData(**data)

    @staticmethod
    def _raise_client_error(exc: ClientError) -> None:
        status_code = getattr(exc, "code", None)

        if status_code in (401, 403):
            raise ValueError("Invalid Gemini API key.") from exc

        if status_code == 429:
            raise RuntimeError("Gemini rate limit reached. Please wait and try again.") from exc

        raise RuntimeError(f"Gemini request failed with status code {status_code}.") from exc


    @staticmethod
    def _parse_response(response_text) -> dict:
        if not response_text or not response_text.strip():
            raise RuntimeError("AI response was empty.")

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise ValueError("AI response must be valid JSON.") from exc

        if not isinstance(data, dict):
            raise ValueError("AI response JSON must be an object.")

        return data

    @staticmethod
    def _validate_doc_text(doc_text: str) -> None:
        if not isinstance(doc_text, str) or not doc_text.strip():
            raise ValueError("Documentation content is required.")

    @staticmethod
    def _validate_skill_data(data: dict) -> None:
        missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
        if missing_fields:
            raise ValueError(f"AI response missing required fields: {', '.join(missing_fields)}.")

        for field in REQUIRED_FIELDS:
            if not isinstance(data[field], str) or not data[field].strip():
                raise ValueError(f"AI response field '{field}' must be a non-empty string.")
            data[field] = data[field].strip()



