def summarize(urgent, info):
    # Bullets-only output: every line starts with "-".
    lines = []

    if urgent:
        for u in urgent:
            src = u.get("source", "") if isinstance(u, dict) else ""
            src_part = f" ({src})" if src else ""
            lines.append(f"- [URGENT] {u.get('client','')}{src_part}: {u.get('message','')}")
    else:
        lines.append("- [URGENT] None")

    if info:
        for i in info:
            src = i.get("source", "") if isinstance(i, dict) else ""
            src_part = f" ({src})" if src else ""
            lines.append(f"- [INFO] {i.get('client','')}{src_part}: {i.get('message','')}")
    else:
        lines.append("- [INFO] None")

    return "\n".join(lines)