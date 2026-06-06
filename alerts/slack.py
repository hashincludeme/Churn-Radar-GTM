import requests
import config


_TIER_EMOJI = {"Healthy": ":large_green_circle:", "At Risk": ":large_yellow_circle:", "Critical": ":red_circle:"}


class SlackNotifier:

    def __init__(self):
        self.webhook_url = config.SLACK_WEBHOOK_URL
        self.dry_run = config.DRY_RUN

    def send_churn_alert(
        self,
        customer_name: str,
        csm_owner: str,
        health_score: float,
        health_tier: str,
        score_delta: float,
        renewal_date: str,
    ) -> bool:
        emoji = _TIER_EMOJI.get(health_tier, ":large_yellow_circle:")
        text = (
            f"{emoji} *Churn Risk Alert — {customer_name}*\n"
            f">Health score dropped *{score_delta:.1f} pts* in the last 7 days "
            f"(now *{health_score:.0f}/100* — _{health_tier}_)\n"
            f">CSM: {csm_owner} | Renewal: {renewal_date}\n"
            f">Action: Create outreach task in HubSpot within 24 hours."
        )

        if self.dry_run:
            print(f"    [DRY RUN] Slack alert:\n      {text.replace(chr(10), chr(10) + '      ')}")
            return True

        resp = requests.post(
            self.webhook_url,
            json={"text": text},
            timeout=10,
        )
        resp.raise_for_status()
        return True

    def send_daily_summary(self, total: int, healthy: int, at_risk: int, critical: int, alerts_fired: int) -> bool:
        text = (
            f":bar_chart: *Daily Health Score Summary*\n"
            f">Total customers scored: *{total}*\n"
            f">:large_green_circle: Healthy: {healthy}  "
            f":large_yellow_circle: At Risk: {at_risk}  "
            f":red_circle: Critical: {critical}\n"
            f">Alerts triggered today: *{alerts_fired}*"
        )

        if self.dry_run:
            print(f"    [DRY RUN] Slack summary:\n      {text.replace(chr(10), chr(10) + '      ')}")
            return True

        resp = requests.post(self.webhook_url, json={"text": text}, timeout=10)
        resp.raise_for_status()
        return True
