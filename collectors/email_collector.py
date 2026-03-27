from __future__ import annotations

import datetime as _dt
import email
import imaplib
import os
from email.header import decode_header
from typing import Any, Dict, List, Optional, Tuple

from config import getenv_first


def _dummy_messages() -> List[Dict[str, Any]]:
    return [
        {
            "source": "email",
            "client": "ABC Pharma",
            "message": "Response needed today: customer approval is pending and the SLA expires tomorrow.",
            "time": "25 mins ago",
        },
        {
            "source": "email",
            "client": "Lumen Retail",
            "message": "FYI: delivery confirmed. No action required.",
            "time": "3 hrs ago",
        },
    ]


def _decode_mime_words(value: Optional[str]) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out = []
    for part, enc in parts:
        if isinstance(part, bytes):
            out.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(part)
    return "".join(out).strip()


def _extract_plain_text(msg: email.message.Message, max_chars: int = 8000) -> str:
    # Prefer plain text parts; fallback to a decoded payload string.
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = part.get("Content-Disposition", "")
            if ctype == "text/plain" and "attachment" not in disp:
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True) or b""
                try:
                    return payload.decode(charset, errors="replace")[:max_chars]
                except Exception:
                    continue
    # Singlepart or no plain part found
    try:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")[:max_chars]
    except Exception:
        pass
    return ""


def fetch_messages(lookback_minutes: float = 30.0) -> List[Dict[str, Any]]:
    """
    Real Email fetching via IMAP (when IMAP_* creds are set), otherwise dummy.
    """
    host = getenv_first("IMAP_HOST", "GMAIL_IMAP_HOST")
    user = getenv_first("IMAP_USER", "IMAP_EMAIL", "GMAIL_USER", "GMAIL_EMAIL")
    password = getenv_first("IMAP_PASS", "IMAP_PASSWORD", "GMAIL_APP_PASSWORD")

    # Convenience defaults for Gmail app-password setups.
    if not host and user and password and user.lower().endswith("@gmail.com"):
        host = "imap.gmail.com"

    if not host or not user or not password:
        return _dummy_messages()

    try:
        port = int(os.getenv("IMAP_PORT", "993"))
        mailbox = os.getenv("IMAP_MAILBOX", "INBOX")
        max_messages = int(os.getenv("IMAP_MAX_MESSAGES", "20"))
        search_unseen = os.getenv("IMAP_SEARCH_UNSEEN", "true").strip().lower() in {"1", "true", "yes", "y"}

        since_dt = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(minutes=float(lookback_minutes))
        since_date = (since_dt.date()).strftime("%d-%b-%Y")  # IMAP SINCE is day-granularity

        imap = imaplib.IMAP4_SSL(host, port)
        imap.login(user, password)
        imap.select(mailbox)

        crit = []
        if search_unseen:
            crit.append("UNSEEN")
        crit.append(f"SINCE {since_date}")
        criteria = " ".join(crit)

        status, data = imap.search(None, criteria)
        if status != "OK":
            return _dummy_messages()

        ids = data[0].split()
        ids = ids[-max_messages:]

        items: List[Dict[str, Any]] = []
        for mid in ids:
            # Fetch RFC822 so we can parse body + headers.
            status, msg_data = imap.fetch(mid, "(RFC822)")
            if status != "OK" or not msg_data:
                continue

            raw = msg_data[0][1]
            if not raw:
                continue

            msg = email.message_from_bytes(raw)
            date_hdr = msg.get("Date")
            try:
                msg_dt = email.utils.parsedate_to_datetime(date_hdr) if date_hdr else None
            except Exception:
                msg_dt = None

            if msg_dt is not None:
                msg_dt_utc = msg_dt.astimezone(_dt.timezone.utc) if msg_dt.tzinfo else msg_dt.replace(tzinfo=_dt.timezone.utc)
                if msg_dt_utc < since_dt:
                    continue

            subject = _decode_mime_words(msg.get("Subject"))
            from_ = _decode_mime_words(msg.get("From"))
            to_ = _decode_mime_words(msg.get("To"))
            plain = _extract_plain_text(msg)

            # "client" heuristic: use first email address in To, else From.
            client = ""
            for part in to_.split(","):
                if "@" in part:
                    client = part.strip()
                    break
            if not client:
                client = from_ or "email"

            time_str = msg_dt.isoformat() if msg_dt else "recent"
            preview = plain.strip().replace("\n", " ")[:500]
            if not preview and subject:
                preview = subject

            items.append(
                {
                    "source": "email",
                    "client": client,
                    "message": f"Subject: {subject}. {preview}".strip(),
                    "time": time_str,
                }
            )

        imap.logout()
        return items if items else _dummy_messages()
    except Exception:
        return _dummy_messages()
