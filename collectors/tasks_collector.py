def fetch_messages(lookback_minutes: float = 30.0):
    # Dummy "task manager" data for assessment/demo (Notion/CSV placeholder).
    # Replace this collector with Notion API or CSV parsing later.
    return [
        {
            "source": "tasks",
            "client": "ABC Pharma",
            "message": "Task due today: send final delivery confirmation to client; waiting for address from operations.",
            "time": "30 mins ago",
        },
        {
            "source": "tasks",
            "client": "Lumen Retail",
            "message": "Task completed: client onboarding checklist finished. Nice work.",
            "time": "4 hrs ago",
        },
    ]

