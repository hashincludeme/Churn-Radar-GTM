import requests
import config


class SalesforceClient:

    def __init__(self):
        self.instance_url = config.SALESFORCE_INSTANCE_URL.rstrip("/")
        self.access_token = config.SALESFORCE_ACCESS_TOKEN
        self.dry_run = config.DRY_RUN

    def update_health_score(self, account_id: str, health_score: float, health_tier: str) -> bool:
        if self.dry_run:
            print(f"    [DRY RUN] Salesforce — account {account_id}: score={health_score}, tier={health_tier}")
            return True

        url = f"{self.instance_url}/services/data/v57.0/sobjects/Account/{account_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "Health_Score__c": health_score,
            "Health_Tier__c": health_tier,
        }
        resp = requests.patch(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return True
