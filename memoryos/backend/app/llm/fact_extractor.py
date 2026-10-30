"""
MemoryOS Backend — Fact Extractor
Uses Gemini to extract structured facts from conversation turns.
Phase 2: Runs after each chat response (non-blocking).
"""

import json
import uuid
import asyncio
from typing import Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("llm.fact_extractor")

_configured = False


def _ensure_configured():
    """Configure the Gemini API key once."""
    global _configured
    if not _configured:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


EXTRACTION_PROMPT = """You are a fact extraction engine for MemoryOS. Analyze the conversation turn below and extract any durable facts, decisions, preferences, or entities mentioned.

## Rules
- Only extract facts that would be useful to remember across sessions
- Don't extract trivial or transient information (greetings, filler)
- Each fact must have a clear type, key, and value
- Set confidence between 0.5 (uncertain/implied) and 1.0 (explicitly stated)
- If no durable facts exist, return an empty array

## Fact Types
- "decision": A choice or decision that was made (e.g., "Use PostgreSQL for the database")
- "preference": A user preference (e.g., "Prefers dark mode")
- "entity": A named entity relevant to the project (e.g., person, tool, service)
- "tech_stack": Technology, framework, or tool being used
- "goal": A project goal or objective
- "milestone": A completed or planned milestone
- "open_question": An unresolved question that needs answering

## Output Format
Return ONLY a JSON array. Each element:
```json
{
  "fact_type": "decision|preference|entity|tech_stack|goal|milestone|open_question",
  "key": "short descriptive label",
  "value": "the fact content",
  "confidence": 0.5 to 1.0
}
```

If no facts found, return: []

## Conversation Turn

**User:** {user_message}

**Assistant:** {assistant_response}

Extract facts now (JSON array only, no markdown fences):"""


async def extract_facts(
    user_message: str,
    assistant_response: str,
    max_retries: int = 2,
) -> list[dict]:
    """
    Extract structured facts from a conversation turn using Gemini.

    Returns a list of fact dicts: [{fact_type, key, value, confidence}, ...]
    Returns empty list on failure (non-blocking — errors shouldn't break chat).
    """
    _ensure_configured()
    settings = get_settings()

    prompt = EXTRACTION_PROMPT.format(
        user_message=user_message[:3000],  # Truncate to avoid token limits
        assistant_response=assistant_response[:3000],
    )

    model = genai.GenerativeModel(
        model_name=settings.llm_model,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=2048,
            temperature=0.1,  # Low temperature for structured extraction
        ),
    )

    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                request_options={"timeout": 30},
            )

            raw_text = response.text.strip()

            # Strip markdown code fences if present
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                # Remove first and last lines (fences)
                lines = [l for l in lines if not l.strip().startswith("```")]
                raw_text = "\n".join(lines).strip()

            facts = json.loads(raw_text)

            if not isinstance(facts, list):
                logger.warning("fact_extraction_not_list", raw=raw_text[:200])
                return []

            # Validate each fact
            valid_facts = []
            valid_types = {
                "decision", "preference", "entity", "tech_stack",
                "goal", "milestone", "open_question",
            }

            for fact in facts:
                if (
                    isinstance(fact, dict)
                    and fact.get("fact_type") in valid_types
                    and fact.get("key")
                    and fact.get("value")
                ):
                    valid_facts.append({
                        "fact_type": fact["fact_type"],
                        "key": str(fact["key"])[:500],
                        "value": str(fact["value"]),
                        "confidence": min(max(float(fact.get("confidence", 0.7)), 0.0), 1.0),
                    })

            logger.info(
                "facts_extracted",
                total_raw=len(facts),
                total_valid=len(valid_facts),
            )
            return valid_facts

        except json.JSONDecodeError as e:
            logger.warning(
                "fact_extraction_json_error",
                attempt=attempt + 1,
                error=str(e)[:150],
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            continue

        except google_exceptions.ResourceExhausted:
            logger.warning("fact_extraction_quota_exhausted")
            return []

        except Exception as e:
            logger.warning(
                "fact_extraction_error",
                attempt=attempt + 1,
                error=str(e)[:150],
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            continue

    return []


async def extract_facts_from_file(
    filename: str,
    file_content: str,
    max_retries: int = 2,
) -> list[dict]:
    """
    Extract structured facts from file content.
    Used when a file is uploaded to also populate structured memory.
    """
    _ensure_configured()
    settings = get_settings()

    prompt = f"""You are a fact extraction engine. Analyze the file below and extract any durable facts.

## File: {filename}

## Content (truncated):
{file_content[:5000]}

## Rules
- Extract technology choices, configuration values, dependencies, and key decisions
- For package.json/requirements.txt: extract tech_stack facts
- For config files: extract relevant settings as preferences
- For markdown docs: extract decisions and goals
- Set confidence based on how explicit the information is

## Output Format
Return ONLY a JSON array. Each element:
{{"fact_type": "decision|preference|entity|tech_stack|goal|milestone|open_question|file_fact", "key": "label", "value": "content", "confidence": 0.5 to 1.0}}

If no facts found, return: []

Extract facts now (JSON array only, no markdown fences):"""

    model = genai.GenerativeModel(
        model_name=settings.llm_model,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=2048,
            temperature=0.1,
        ),
    )

    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                request_options={"timeout": 30},
            )

            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                raw_text = "\n".join(lines).strip()

            facts = json.loads(raw_text)
            if not isinstance(facts, list):
                return []

            valid_types = {
                "decision", "preference", "entity", "tech_stack",
                "goal", "milestone", "open_question", "file_fact",
            }

            valid_facts = []
            for fact in facts:
                if (
                    isinstance(fact, dict)
                    and fact.get("fact_type") in valid_types
                    and fact.get("key")
                    and fact.get("value")
                ):
                    valid_facts.append({
                        "fact_type": fact["fact_type"],
                        "key": str(fact["key"])[:500],
                        "value": str(fact["value"]),
                        "confidence": min(max(float(fact.get("confidence", 0.7)), 0.0), 1.0),
                    })

            logger.info(
                "file_facts_extracted",
                filename=filename,
                total_valid=len(valid_facts),
            )
            return valid_facts

        except json.JSONDecodeError:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            continue
        except google_exceptions.ResourceExhausted:
            return []
        except Exception as e:
            logger.warning("file_fact_extraction_error", error=str(e)[:150])
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            continue

    return []
