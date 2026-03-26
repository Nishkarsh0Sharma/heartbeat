import schedule
import time

from collectors.slack_collector import fetch_messages as fetch_slack_messages
from collectors.email_collector import fetch_messages as fetch_email_messages
from collectors.jira_collector import fetch_messages as fetch_jira_messages
from collectors.github_collector import fetch_messages as fetch_github_messages
from collectors.tasks_collector import fetch_messages as fetch_tasks_messages
from processing.digest import make_digest
from delivery.notifier import send_notification
from utils.activity import is_laptop_active
from config import (
    HEARTBEAT_INTERVAL_MINUTES,
    HEARTBEAT_REQUIRE_ACTIVE,
    HEARTBEAT_NOTIFICATION_ENABLED,
)


def run_once():
    print("Running heartbeat...")

    if HEARTBEAT_REQUIRE_ACTIVE and not is_laptop_active():
        print("Laptop inactive (idle/lock). Skipping digest + notification.")
        return

    lookback_minutes = float(HEARTBEAT_INTERVAL_MINUTES)

    # Merge events from multiple sources into a single list.
    messages = []
    messages.extend(fetch_slack_messages(lookback_minutes=lookback_minutes))
    messages.extend(fetch_email_messages(lookback_minutes=lookback_minutes))
    messages.extend(fetch_jira_messages(lookback_minutes=lookback_minutes))
    messages.extend(fetch_github_messages(lookback_minutes=lookback_minutes))
    messages.extend(fetch_tasks_messages(lookback_minutes=lookback_minutes))

    # Keep digest short and predictable.
    messages = messages[:50]
    digest = make_digest(messages)

    print("\n===== DIGEST =====")
    print(digest)

    if HEARTBEAT_NOTIFICATION_ENABLED:
        send_notification(digest)


def main_loop(interval_minutes: float = HEARTBEAT_INTERVAL_MINUTES):
    # schedule library expects minutes; using float keeps it configurable.
    schedule.every(interval_minutes).minutes.do(run_once)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Heartbeat digest script")
    parser.add_argument("--once", action="store_true", help="Run a single heartbeat and exit")
    parser.add_argument(
        "--interval-minutes",
        type=float,
        default=HEARTBEAT_INTERVAL_MINUTES,
        help="Heartbeat interval in minutes (default: config)",
    )
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        main_loop(args.interval_minutes)