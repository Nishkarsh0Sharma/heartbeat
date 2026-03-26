import subprocess

from config import NOTIFICATION_MAX_CHARS


def _to_single_line(text: str) -> str:
    # AppleScript quoting breaks easily with newlines; notifications work better as a single line.
    return " ".join(text.splitlines()).strip()


def send_notification(text: str) -> None:
    short = _to_single_line(text)
    if len(short) > NOTIFICATION_MAX_CHARS:
        short = short[:NOTIFICATION_MAX_CHARS].rstrip()

    # Escape quotes for AppleScript string literal.
    short = short.replace('"', '\\"')

    # Run without shell=True to avoid quoting issues.
    subprocess.run(
        ["osascript", "-e", f'display notification "{short}" with title "Heartbeat"'],
        check=False,
    )