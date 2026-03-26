from __future__ import annotations

import datetime as _dt
import os
from typing import Any, Dict, List, Optional


def _dummy_messages() -> List[Dict[str, Any]]:
    return [
        {
            "source": "github",
            "client": "ABC Pharma",
            "message": "PR #52 requires your review before merge (due today).",
            "time": "15 mins ago",
        },
        {
            "source": "github",
            "client": "Lumen Retail",
            "message": "Issue #19 updated. Tests are passing. FYI.",
            "time": "2 hrs ago",
        },
    ]


def _iso_utc(dt: _dt.datetime) -> str:
    return dt.astimezone(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_messages(lookback_minutes: float = 30.0) -> List[Dict[str, Any]]:
    """
    Real GitHub fetching via REST Search API (when GITHUB_* creds are set), otherwise dummy.
    """
    token = os.getenv("GITHUB_TOKEN", "").strip()
    username = os.getenv("GITHUB_USERNAME", "").strip()
    if not token or not username:
        return _dummy_messages()

    try:
        import requests
    except ImportError:
        return _dummy_messages()

    max_results = int(os.getenv("GITHUB_MAX_RESULTS", "20"))
    repos = os.getenv("GITHUB_REPOS", "").strip()
    repo_filter = ""
    if repos:
        repo_first = [r.strip() for r in repos.split(",") if r.strip()][0]
        if repo_first:
            repo_filter = f" repo:{repo_first}"

    since_dt = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(minutes=float(lookback_minutes))
    since_str = _iso_utc(since_dt)

    # Search includes PRs + issues; keep results open items updated recently.
    q = f"assignee:{username}{repo_filter} is:open updated:>={since_str}"

    try:
        url = "https://api.github.com/search/issues"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "heartbeat-script",
        }
        resp = requests.get(url, params={"q": q, "per_page": max_results}, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        items_raw = data.get("items", []) or []

        items: List[Dict[str, Any]] = []
        for it in items_raw:
            title = it.get("title") or ""
            updated_at = it.get("updated_at") or ""
            state = it.get("state") or ""
            html_url = it.get("html_url") or ""

            repo_url = it.get("repository_url") or ""
            # repo_url: https://api.github.com/repos/owner/name
            client = "github"
            parts = repo_url.split("/repos/")
            if len(parts) == 2:
                client = parts[1]

            type_part = "PR" if it.get("pull_request") else "Issue"
            items.append(
                {
                    "source": "github",
                    "client": client,
                    "message": f"{type_part}: {title}. State: {state}.",
                    "time": updated_at,
                    "url": html_url or None,
                }
            )

        return items if items else _dummy_messages()
    except Exception:
        return _dummy_messages()

