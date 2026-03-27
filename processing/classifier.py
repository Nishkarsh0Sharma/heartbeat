def classify(messages):
    urgent = []
    info = []

    for msg in messages:
        text = (msg.get("message") or "").lower()
        is_urgent = any(
            kw in text
            for kw in [
                "asap",
                "important",
                "urgent",
                "blocked",
                "blocker",
                "overdue",
                "due today",
                "due soon",
                "deadline",
                "waiting for",
                "approval",
                "need your response",
                "need response",
                "stuck",
                "approval needed",
            ]
        )

        if is_urgent:
            urgent.append(msg)
        else:
            info.append(msg)

    return urgent, info
