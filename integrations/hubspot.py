import requests
import config


class HubSpotClient:
    BASE = "https://api.hubapi.com"

    def __init__(self):
        self.api_key = config.HUBSPOT_API_KEY
        self.dry_run = config.DRY_RUN

    def update_health_score(self, contact_id: str, health_score: float, health_tier: str) -> bool:
        if self.dry_run:
            print(f"    [DRY RUN] HubSpot — contact {contact_id}: score={health_score}, tier={health_tier}")
            return True

        url = f"{self.BASE}/crm/v3/objects/contacts/{contact_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "properties": {
                "health_score": str(health_score),
                "health_tier": health_tier,
            }
        }
        resp = requests.patch(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return True

    def create_cs_task(self, contact_id: str, customer_name: str, csm_owner: str, score_delta: float) -> bool:
        if self.dry_run:
            print(f"    [DRY RUN] HubSpot — task created for {customer_name} ({csm_owner}), delta={score_delta:.1f}pts")
            return True

        url = f"{self.BASE}/crm/v3/objects/tasks"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "properties": {
                "hs_task_subject": f"Churn Risk Outreach — {customer_name}",
                "hs_task_body": (
                    f"Health score dropped {score_delta:.1f} pts in the last 7 days. "
                    f"Initiate proactive outreach within 24 hours."
                ),
                "hs_task_status": "NOT_STARTED",
                "hs_task_priority": "HIGH",
                "hubspot_owner_id": csm_owner,
            },
            "associations": [
                {
                    "to": {"id": contact_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 204}],
                }
            ],
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return True
