# Heartbeat (Client Digest)

This script runs on a Mac and shows the founder a short digest every 30 minutes while the laptop is active.

## Run once (debug / validate)
```bash
cd <project-directory>
./venv/bin/python main.py --once
```

You should see `===== DIGEST =====` printed in the terminal. A macOS notification is also attempted.

## Run continuously
```bash
HEARTBEAT_INTERVAL_MINUTES=30 ./venv/bin/python main.py
```

## Environment variables
- `HEARTBEAT_INTERVAL_MINUTES` (default `30`)
- `HEARTBEAT_REQUIRE_ACTIVE` (default `false`)
- `HEARTBEAT_IDLE_THRESHOLD_SECONDS` (default `60`)
- `HEARTBEAT_NOTIFICATION_ENABLED` (default `true`)
- `HEARTBEAT_LLM_PROVIDER` (default `mock`, set to `claude` to enable Claude)
- `CLAUDE_MODEL` (default `claude-3-5-sonnet-latest`)
- `LLM_TEMPERATURE` (default `0.2`)

Credential aliases supported:
- Claude key: `ANTHROPIC_API_KEY` or `CLAUDE_API_KEY`
- GitHub token: `GITHUB_TOKEN` or `GH_TOKEN` or `GITHUB_PAT`
- GitHub user: `GITHUB_USERNAME` or `GITHUB_USER`
- IMAP user: `IMAP_USER` or `IMAP_EMAIL` or `GMAIL_USER` or `GMAIL_EMAIL`
- IMAP password: `IMAP_PASS` or `IMAP_PASSWORD` or `GMAIL_APP_PASSWORD`
- IMAP host: `IMAP_HOST` or `GMAIL_IMAP_HOST` (auto-defaults to `imap.gmail.com` for `@gmail.com`)

## How data is gathered
Collectors (`slack_collector`, `email_collector`, `jira_collector`, `github_collector`, `tasks_collector`) have:
- dummy fallback (works without credentials)
- real API mode (enabled by environment variables listed below)

## Enable Claude (optional)
For assessment/demo, keep `HEARTBEAT_LLM_PROVIDER=mock` (default).

To enable real Claude calls:
```bash
cd <project-directory>
export ANTHROPIC_API_KEY="YOUR_KEY"
export HEARTBEAT_LLM_PROVIDER="claude"
./venv/bin/python main.py --once
```

## Enable Real API fetching (optional)
Your demo works with dummy data even without any credentials.

When you set the following environment variables, collectors will fetch real recent items instead of dummy.

- Slack: `SLACK_BOT_TOKEN` (or `SLACK_TOKEN`), optionally `SLACK_CHANNEL_IDS` (comma-separated), optionally `SLACK_HISTORY_LIMIT`
- Jira: `JIRA_BASE_URL`, `JIRA_EMAIL` (or `JIRA_USER`), `JIRA_API_TOKEN`, optionally `JIRA_PROJECT_KEYS` and `JIRA_JQL`
- GitHub: `GITHUB_TOKEN`, `GITHUB_USERNAME`, optionally `GITHUB_REPOS` (comma-separated `owner/repo`)
- Email (IMAP): `IMAP_HOST`, `IMAP_USER`, `IMAP_PASS`, optionally `IMAP_MAILBOX`, `IMAP_MAX_MESSAGES`

## Security note
- Never commit real tokens/passwords to git.
- If any token was exposed in chat/screenshots, rotate it immediately in provider settings.
