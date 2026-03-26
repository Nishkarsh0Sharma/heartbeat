import subprocess

import re

from typing import Optional

from config import HEARTBEAT_IDLE_THRESHOLD_SECONDS


def _get_idle_time_seconds() -> Optional[float]:
    """
    HIDIdleTime from IOHIDSystem is reported in nanoseconds.
    Returns idle time in seconds, or None if it can't be determined.
    """
    try:
        out = subprocess.check_output(["ioreg", "-c", "IOHIDSystem"], text=True, stderr=subprocess.DEVNULL)
        m = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', out)
        if not m:
            return None
        idle_ns = int(m.group(1))
        return idle_ns / 1_000_000_000
    except Exception:
        return None


def is_laptop_active() -> bool:
    # If we can't reliably detect idle time, fail open (run heartbeat).
    idle_seconds = _get_idle_time_seconds()
    if idle_seconds is None:
        return True

    return idle_seconds < HEARTBEAT_IDLE_THRESHOLD_SECONDS