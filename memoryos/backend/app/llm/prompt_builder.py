"""
MemoryOS Backend — Prompt Builder
Assembles the system prompt + retrieved context + user message
for the Gemini LLM call. Architecture.md §2.1.
"""

from app.core.logging import get_logger

logger = get_logger("llm.prompt_builder")

# The Master System Prompt — Phase 1 rules active:
# RULE-1 (always use memory), RULE-2 (cite sources),
# RULE-4 (maintain consistency), RULE-5 (be honest about uncertainty),
# RULE-7 (user isolation), RULE-8 (never hallucinate memory)
SYSTEM_PROMPT = """You are MemoryOS — an AI assistant with persistent, project-scoped memory.

## Your Core Capabilities
You have access to the full conversation history and semantic memory of this project.
When answering, you MUST draw on relevant past context to provide continuity.

## Rules You Must Follow

RULE-1: ALWAYS USE MEMORY
- Before answering any question, check if relevant context exists in the retrieved
  memory chunks provided below. Use it to inform your response.
- If memory is relevant, weave it naturally into your answer — don't just dump it.

RULE-2: CITE YOUR SOURCES
- When referencing past conversations or facts from memory, briefly note the source
  (e.g., "As discussed earlier..." or "Based on your previous decision...").
- This builds trust and lets the user verify.

RULE-4: MAINTAIN CONSISTENCY
- Never contradict information from memory unless the user explicitly updates it.
- If you notice a potential contradiction, surface it: "I notice this may conflict
  with [previous fact]. Would you like to update it?"

RULE-5: BE HONEST ABOUT UNCERTAINTY
- If retrieved memory is sparse or old, say so: "Based on limited context from
  our earlier discussion..."
- Never fabricate memory or pretend to recall something you don't have evidence for.

RULE-7: RESPECT ISOLATION
- Only use memory from this specific project. Never reference or leak information
  from other projects or users.

RULE-8: NEVER HALLUCINATE MEMORY
- If no relevant memory exists, say so honestly. Don't invent past conversations
  or facts that weren't stored.

## Response Style
- Be helpful, precise, and professional.
- Use code blocks for code. Use markdown for structure.
- Be concise but thorough — this is a working tool, not a chatbot.
"""


def build_prompt(
    user_message: str,
    retrieved_chunks: list[dict],
    recent_history: list[dict],
    project_name: str = "",
    project_context: str = "",
) -> tuple[str, str]:
    """
    Build the full prompt for Gemini.

    Returns:
        (system_instruction, user_prompt) — both strings.

    Architecture:
        system_instruction = SYSTEM_PROMPT + project context
        user_prompt = retrieved memory + recent history + new message
    """
    # Build system instruction with project context
    system_instruction = SYSTEM_PROMPT
    if project_name:
        system_instruction += f"\n\n## Current Project: {project_name}\n"
    if project_context:
        system_instruction += f"{project_context}\n"

    # Build the user prompt
    parts = []

    # Section 1: Retrieved memory context
    if retrieved_chunks:
        parts.append("## Retrieved Memory Context")
        parts.append(
            "The following are relevant memories retrieved from this project's history:\n"
        )
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source_type", "conversation")
            score = chunk.get("combined_score", chunk.get("score", 0))
            content = chunk.get("content", "")
            parts.append(
                f"**Memory {i}** (source: {source}, relevance: {score:.2f}):\n{content}\n"
            )
        parts.append("---\n")

    # Section 2: Recent conversation history (for continuity)
    if recent_history:
        parts.append("## Recent Conversation History")
        for turn in recent_history[-10:]:  # Last 10 turns max
            role = turn.get("role", "user")
            content = turn.get("content", "")
            # Truncate long turns to save token budget
            if len(content) > 500:
                content = content[:500] + "..."
            parts.append(f"**{role.capitalize()}**: {content}\n")
        parts.append("---\n")

    # Section 3: The current user message
    parts.append("## Current Message")
    parts.append(f"{user_message}")

    user_prompt = "\n".join(parts)

    logger.info(
        "prompt_built",
        retrieved_chunks=len(retrieved_chunks),
        history_turns=len(recent_history),
        prompt_length=len(user_prompt),
    )

    return system_instruction, user_prompt
