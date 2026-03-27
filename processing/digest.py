from __future__ import annotations

from typing import Any

from config import HEARTBEAT_LLM_PROVIDER, getenv_first
from processing.classifier import classify as rule_classify
from processing.summarizer import summarize as rule_summarize


def _rule_digest(messages: list[dict[str, Any]], reason: str) -> str:
    print(f"Summarizer: rule-based ({reason})")
    urgent, info = rule_classify(messages)
    return rule_summarize(urgent, info)


def make_digest(messages: list[dict[str, Any]]) -> str:
    """
    Build the digest text.

    - Default: rule-based summarize + classify (works without credentials).
    - If HEARTBEAT_LLM_PROVIDER=claude and ANTHROPIC_API_KEY is set: use Claude.
    """
    if HEARTBEAT_LLM_PROVIDER != "claude":
        return _rule_digest(messages, "provider disabled")

    # Only attempt real Claude calls when a key exists.
    if not getenv_first("ANTHROPIC_API_KEY", "CLAUDE_API_KEY"):
        return _rule_digest(messages, "missing API key")

    # Lazy import so mock mode doesn't require anthropic dependency.
    from llm.claude_client import build_urgent_info_from_claude

    try:
        print("Summarizer: Claude")
        urgent, info = build_urgent_info_from_claude(messages)
    except Exception as exc:
        # Keep the heartbeat usable when the API is down, misconfigured, or out of credits.
        return _rule_digest(messages, f"Claude unavailable: {type(exc).__name__}")

    return rule_summarize(urgent, info)
