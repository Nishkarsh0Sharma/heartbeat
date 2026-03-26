import os

# How often to run the heartbeat (minutes).
HEARTBEAT_INTERVAL_MINUTES = float(os.getenv("HEARTBEAT_INTERVAL_MINUTES", "30"))

# If true, skip heartbeat when the laptop looks idle (locked/asleep -> fewer notifications).
# Default is false so you can validate the system quickly.
HEARTBEAT_REQUIRE_ACTIVE = os.getenv("HEARTBEAT_REQUIRE_ACTIVE", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
}

# Consider the laptop "active" when user idle time is below this threshold.
HEARTBEAT_IDLE_THRESHOLD_SECONDS = float(os.getenv("HEARTBEAT_IDLE_THRESHOLD_SECONDS", "60"))

# Enable/disable macOS notifications.
HEARTBEAT_NOTIFICATION_ENABLED = os.getenv("HEARTBEAT_NOTIFICATION_ENABLED", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
}

# Keep notifications short (AppleScript strings are easier when single-line).
NOTIFICATION_MAX_CHARS = int(os.getenv("NOTIFICATION_MAX_CHARS", "240"))

# LLM (Claude) settings
#
# For assessment/demo without credentials, keep this as "mock" (default).
# Set to "claude" and provide ANTHROPIC_API_KEY to enable real LLM calls.
HEARTBEAT_LLM_PROVIDER = os.getenv("HEARTBEAT_LLM_PROVIDER", "mock").strip().lower()
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

