import os
import pandas as pd

import config
from scoring.calculator import compute_scores, detect_drops
from integrations.hubspot import HubSpotClient
from integrations.salesforce import SalesforceClient
from alerts.slack import SlackNotifier

DATA_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "customers.csv")


def main():
    mode = "DRY RUN" if config.DRY_RUN else "LIVE"
    print(f"\n{'='*62}")
    print(f"  Churn Radar — {mode} MODE")
    print(f"  Alert threshold : {config.ALERT_THRESHOLD_PCT:.0f}% drop over {config.TREND_WINDOW_DAYS} days")
    print(f"{'='*62}")

    # ── Step 1: Load customers ────────────────────────────────────────
    print("\n[1/4] Loading customer data...")
    df = pd.read_csv(DATA_PATH)
    print(f"      {len(df)} customers loaded.")

    # ── Step 2: Calculate health scores ──────────────────────────────
    print("\n[2/4] Calculating health scores...")
    df = compute_scores(df)
    df = detect_drops(df)

    tier_counts = df["health_tier"].value_counts().to_dict()
    healthy = tier_counts.get("Healthy", 0)
    at_risk = tier_counts.get("At Risk", 0)
    critical = tier_counts.get("Critical", 0)
    alerts = df["alert_triggered"].sum()

    print(f"      Healthy: {healthy}  |  At Risk: {at_risk}  |  Critical: {critical}")
    print(f"      Alerts to fire: {alerts}")

    # ── Step 3: Push scores to HubSpot + Salesforce ───────────────────
    print("\n[3/4] Syncing health scores to HubSpot & Salesforce...")
    hs = HubSpotClient()
    sf = SalesforceClient()
    slack = SlackNotifier()

    for _, row in df.iterrows():
        hs.update_health_score(row["hubspot_contact_id"], row["health_score"], row["health_tier"])
        sf.update_health_score(row["salesforce_account_id"], row["health_score"], row["health_tier"])

    # ── Step 4: Fire Slack alerts for at-risk customers ───────────────
    print("\n[4/4] Sending Slack alerts for triggered accounts...")
    alerted = df[df["alert_triggered"]]

    if alerted.empty:
        print("      No alerts triggered today.")
    else:
        for _, row in alerted.iterrows():
            slack.send_churn_alert(
                customer_name=row["customer_name"],
                csm_owner=row["csm_owner"],
                health_score=row["health_score"],
                health_tier=row["health_tier"],
                score_delta=row["score_delta"],
                renewal_date=row["renewal_date"],
            )
            hs.create_cs_task(
                contact_id=row["hubspot_contact_id"],
                customer_name=row["customer_name"],
                csm_owner=row["csm_owner"],
                score_delta=row["score_delta"],
            )

    slack.send_daily_summary(len(df), healthy, at_risk, critical, int(alerts))

    # ── Summary table ──────────────────────────────────────────────────
    print("\n" + "-" * 62)
    print(f"  {'Customer':<22} {'Score':>6}  {'Tier':<10}  {'Delta':>7}  {'Alert'}")
    print("-" * 62)
    for _, row in df.sort_values("health_score").iterrows():
        flag = "  *** ALERT" if row["alert_triggered"] else ""
        print(
            f"  {row['customer_name']:<22} {row['health_score']:>6.1f}  "
            f"{row['health_tier']:<10}  {row['score_delta']:>+6.1f}  {flag}"
        )
    print("-" * 62)
    print(f"\n  Done. {int(alerts)} alert(s) fired, {len(df)} customers scored.\n")


if __name__ == "__main__":
    main()
