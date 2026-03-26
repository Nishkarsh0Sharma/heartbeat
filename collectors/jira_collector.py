from __future__ import annotations

import os
from typing import Any, Dict, List


def _dummy_messages() -> List[Dict[str, Any]]:
    return [
        {
            "source": "jira",
            "client": "ABC Pharma",
            "message": "JIRA-214 is overdue. Blocked by legal approval. Waiting for your response.",
            "time": "1 hr ago",
        },
        {
            "source": "jira",
            "client": "Lumen Retail",
            "message": "JIRA-88 status updated to In Progress. No action needed right now.",
            "time": "40 mins ago",
        },
    ]


def fetch_messages(lookback_minutes: float = 30.0) -> List[Dict[str, Any]]:
    """
    Real Jira fetching via REST (when JIRA_* creds are set), otherwise dummy.
    """
    base_url = os.getenv("JIRA_BASE_URL", "").strip().rstrip("/")
    user = os.getenv("JIRA_EMAIL", "").strip() or os.getenv("JIRA_USER", "").strip()
    token = os.getenv("JIRA_API_TOKEN", "").strip()

    if not base_url or not user or not token:
        return _dummy_messages()

    try:
        import requests
    except ImportError:
        return _dummy_messages()

    max_results = int(os.getenv("JIRA_MAX_RESULTS", "20"))
    jql = os.getenv("JIRA_JQL", "").strip()
    if not jql:
        mins = max(1, int(float(lookback_minutes)))
        project_keys = os.getenv("JIRA_PROJECT_KEYS", "").strip()
        project_part = f" AND project in ({project_keys})" if project_keys else ""
        jql = f"updated >= -{mins}m{project_part} ORDER BY updated DESC"

    fields = "summary,status,duedate,labels,priority,updated,project,assignee"

    try:
        resp = requests.get(
            f"{base_url}/rest/api/3/search",
            params={"jql": jql, "maxResults": max_results, "fields": fields},
            auth=(user, token),
            timeout=30,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()
        issues = data.get("issues", [])

        items: List[Dict[str, Any]] = []
        for issue in issues:
            key = issue.get("key", "")
            fields_obj = issue.get("fields", {}) or {}
            project = (fields_obj.get("project") or {}).get("key") or "jira"
            summary = fields_obj.get("summary") or ""
            status = (fields_obj.get("status") or {}).get("name") or ""
            due = fields_obj.get("duedate") or ""
            labels = fields_obj.get("labels") or []
            updated = fields_obj.get("updated") or ""

            label_part = f" Labels: {', '.join(labels)}." if labels else ""
            due_part = f" Due: {due}." if due else ""

            items.append(
                {
                    "source": "jira",
                    "client": project,
                    "message": f"{key}: {summary} Status: {status}.{due_part}{label_part}".strip(),
                    "time": updated or "recent",
                    "url": f"{base_url}/browse/{key}" if key else None,
                }
            )

        return items if items else _dummy_messages()
    except Exception:
        return _dummy_messages()

