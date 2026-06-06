# Churn Radar

Early-warning system for B2B SaaS churn. Calculates a daily health score per customer from product-usage signals, syncs the score to HubSpot and Salesforce, and fires Slack alerts + CS tasks the moment a customer shows a significant drop.

## Problem
Customers go from healthy to churned in <60 days. By the time CS notices a missed renewal or offboarding request, the relationship is unsalvageable. Login frequency, feature adoption, and support-ticket volume are invisible until it's too late.

## How it works

```
Product analytics (Mixpanel / Amplitude)
          │
          ▼
  n8n daily pull → main.py
          │
          ├── Scoring engine (scoring/calculator.py)
          │     Login frequency  30 pts
          │     Feature adoption 30 pts
          │     Support tickets  20 pts
          │     NPS              20 pts
          │     ─────────────── 100 pts
          │
          ├── HubSpot (integrations/hubspot.py)
          │     • Update contact health score + tier
          │     • Create CS task if alert triggered
          │
          ├── Salesforce (integrations/salesforce.py)
          │     • Update Account.Health_Score__c
          │
          └── Slack (alerts/slack.py)
                • Per-account alert when score drops ≥20 pts in 7 days
                • Daily summary digest
```

## Health tiers

| Score  | Tier     |
|--------|----------|
| 75–100 | Healthy  |
| 50–74  | At Risk  |
| 0–49   | Critical |

## Quickstart

```bash
pip install -r requirements.txt

# Run in dry-run mode (no real API calls)
python main.py

# Run against real integrations
cp .env.example .env
# fill in credentials, then:
DRY_RUN=false python main.py
```

## Configuration (`.env`)

| Variable              | Default | Description                                   |
|-----------------------|---------|-----------------------------------------------|
| `HUBSPOT_API_KEY`     | —       | HubSpot private app token                     |
| `SALESFORCE_INSTANCE_URL` | — | `https://yourorg.salesforce.com`              |
| `SALESFORCE_ACCESS_TOKEN` | — | OAuth access token                            |
| `SLACK_WEBHOOK_URL`   | —       | Slack incoming webhook URL                    |
| `DRY_RUN`             | `true`  | `false` to hit live APIs                      |
| `ALERT_THRESHOLD_PCT` | `20`    | Point drop in 7 days that triggers an alert   |
| `TREND_WINDOW_DAYS`   | `7`     | Lookback window for trend detection           |

## Automation boundary

| Automatable | Not automatable |
|---|---|
| Usage data aggregation | Customer conversation to understand churn drivers |
| Health score calculation | Relationship rebuilding |
| Low-health Slack alerts | Negotiating renewal terms |
| HubSpot CS task creation | |
| Salesforce field sync | |

## Project structure

```
churn-radar/
├── main.py                   # Orchestrator
├── config.py                 # Env var config + dry-run flag
├── scoring/
│   └── calculator.py         # Health score formula + trend detection
├── integrations/
│   ├── hubspot.py            # Score sync + CS task creation
│   └── salesforce.py        # Health_Score__c field update
├── alerts/
│   └── slack.py              # Per-account alerts + daily summary
├── sample_data/
│   └── customers.csv         # Mock data for dry-run
└── .env.example
```
