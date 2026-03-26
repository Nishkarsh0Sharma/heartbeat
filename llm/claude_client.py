from __future__ import annotations

import json
import os
from typing import Any

from config import CLAUDE_MODEL, LLM_TEMPERATURE


def build_urgent_info_from_claude(
    messages: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Ask Claude to classify each message into:
    - urgent: needs founder action soon
    - info: FYIs and non-urgent updates

    We require Claude to return strict JSON so parsing is reliable.
    """
    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is required for claude mode")

    client = Anthropic(api_key=api_key)

    # Keep the prompt compact; digest runs frequently.
    user_items = []
    for m in messages[:25]:
        user_items.append(
            {
                "client": m.get("client", ""),
                "message": m.get("message", ""),
                "time": m.get("time", ""),
                "source": m.get("source", ""),
            }
        )

    system_prompt = (
        "You generate a short digest for a non-technical founder. "
        "Classify messages into urgent vs informational and produce concise summaries. "
        "Urgent means the founder likely needs to reply, unblock, or act today/soon. "
        "Return ONLY valid JSON in the specified format."
    )

    prompt = {
        "format": {
            "urgent": [{"client": "string", "message": "string", "source": "string"}],
            "info": [{"client": "string", "message": "string", "source": "string"}],
        },
        "messages": user_items,
        "rules": [
            "Mark urgent if the text includes ASAP, urgent, blocker, stuck, waiting, approval needed, or an explicit deadline.",
            "Mark urgent if the message asks for a decision/response from the founder.",
            "Otherwise mark as info.",
        ],
    }

    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=800,
        temperature=LLM_TEMPERATURE,
        system=system_prompt,
        messages=[{"role": "user", "content": json.dumps(prompt)}],
    )

    # Claude SDK typically returns content blocks; we take the first text block.
    content = resp.content[0].text if resp.content else ""
    data = json.loads(content)

    urgent = data.get("urgent", [])
    info = data.get("info", [])
    # Ensure schema matches what summarizer expects.
    urgent = [
        {"client": u.get("client", ""), "message": u.get("message", ""), "source": u.get("source", "")}
        for u in urgent
    ]
    info = [
        {"client": i.get("client", ""), "message": i.get("message", ""), "source": i.get("source", "")}
        for i in info
    ]
    return urgent, info

