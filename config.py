import os
from dotenv import load_dotenv

load_dotenv()

# External integrations
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY", "")
SALESFORCE_INSTANCE_URL = os.getenv("SALESFORCE_INSTANCE_URL", "")
SALESFORCE_ACCESS_TOKEN = os.getenv("SALESFORCE_ACCESS_TOKEN", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Default True — runs end-to-end without real credentials
DRY_RUN = os.getenv("DRY_RUN", "true").lower() != "false"

# Health score drop threshold to trigger an alert (percentage points)
ALERT_THRESHOLD_PCT = float(os.getenv("ALERT_THRESHOLD_PCT", "20"))

# Lookback window for trend detection (days)
TREND_WINDOW_DAYS = int(os.getenv("TREND_WINDOW_DAYS", "7"))
