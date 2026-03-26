from __future__ import annotations

import datetime as _dt
import os
from typing import Any, Dict, List, Optional


def _dummy_messages() -> List[Dict[str, Any]]:
    return [
        {
            "source": "slack",
            "client": "ABC Pharma",
            "message": "Need an update ASAP — are we blocked on approval?",
            "time": "2 hrs ago",
        },
        {
            "source": "slack",
            "client": "XYZ CA",
            "message": "Project looks good. No action needed. FYI.",
            "time": "10 mins ago",
        },
    ]


def _iso_now(ts: float) -> str:
    return _dt.datetime.fromtimestamp(ts).astimezone().isoformat(timespec="minutes")


def fetch_messages(lookback_minutes: float = 30.0) -> List[Dict[str, Any]]:
    """
    Real Slack fetching (when SLACK_BOT_TOKEN/SLACK_TOKEN is set), otherwise dummy.

    Normalized output fields:
      - source, client, message, time, url(optional)
    """
    token = (os.getenv("SLACK_BOT_TOKEN") or os.getenv("SLACK_TOKEN") or "").strip()
    if not token:
        return _dummy_messages()

    try:
        import requests
    except ImportError:
        return _dummy_messages()

    since_ts = _dt.datetime.now().timestamp() - (lookback_minutes * 60.0)
    oldest = str(since_ts)

    # Optional: restrict fetch to specific channels to reduce noise.
    # Comma-separated channel IDs, e.g. C0123..., D0456...
    channel_ids_env = os.getenv("SLACK_CHANNEL_IDS", "").strip()

    api_base = "https://slack.com/api"
    headers = {"Authorization": f"Bearer {token}"}

    def slack_api(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.get(f"{api_base}/{method}", params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    try:
        channels: List[Dict[str, Any]] = []

        if channel_ids_env:
            for cid in [c.strip() for c in channel_ids_env.split(",") if c.strip()]:
                channels.append({"id": cid, "name": cid})
        else:
            # Best-effort: list a limited number of conversations and then fetch history.
            list_limit = int(os.getenv("SLACK_FETCH_CHANNELS_LIMIT", "10"))
            list_types = os.getenv("SLACK_FETCH_TYPES", "public_channel,private_channel,im")
            res = slack_api("conversations.list", {"limit": list_limit, "types": list_types})
            if not res.get("ok"):
                return _dummy_messages()
            channels = res.get("channels", [])[:list_limit]

        items: List[Dict[str, Any]] = []
        history_limit = int(os.getenv("SLACK_HISTORY_LIMIT", "50"))

        for ch in channels:
            channel_id = ch.get("id")
            if not channel_id:
                continue

            res = slack_api(
                "conversations.history",
                {
                    "channel": channel_id,
                    "oldest": oldest,
                    "limit": history_limit,
                },
            )
            if not res.get("ok"):
                continue

            channel_name = ch.get("name") or channel_id
            for m in res.get("messages", []):
                text = (m.get("text") or "").strip()
                if not text:
                    continue

                ts_raw = m.get("ts")
                ts_val = float(ts_raw) if ts_raw else since_ts

                items.append(
                    {
                        "source": "slack",
                        "client": channel_name,
                        "message": text,
                        "time": _iso_now(ts_val),
                        # Slack ts links are a bit more involved; keep url optional.
                    }
                )

        return items if items else _dummy_messages()
    except Exception:
        # Don't fail the whole heartbeat when API is misconfigured.
        return _dummy_messages()