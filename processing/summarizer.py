MAX_URGENT_ITEMS = 5
MAX_INFO_ITEMS = 5


def _dedupe_messages(items):
    seen = set()
    out = []

    for item in items:
        key = (
            item.get("source", "") if isinstance(item, dict) else "",
            item.get("client", "") if isinstance(item, dict) else "",
            item.get("message", "") if isinstance(item, dict) else "",
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(item)

    return out


def _format_lines(items, label, limit):
    lines = []
    deduped = _dedupe_messages(items)

    for item in deduped[:limit]:
        src = item.get("source", "") if isinstance(item, dict) else ""
        src_part = f" ({src})" if src else ""
        lines.append(f"- [{label}] {item.get('client','')}{src_part}: {item.get('message','')}")

    remaining = len(deduped) - min(len(deduped), limit)
    if remaining > 0:
        lines.append(f"- [{label}] {remaining} more items not shown")

    return lines


def summarize(urgent, info):
    # Bullets-only output: every line starts with "-".
    lines = []

    if urgent:
        lines.extend(_format_lines(urgent, "URGENT", MAX_URGENT_ITEMS))
    else:
        lines.append("- [URGENT] None")

    if info:
        lines.extend(_format_lines(info, "INFO", MAX_INFO_ITEMS))
    else:
        lines.append("- [INFO] None")

    return "\n".join(lines)
