import pandas as pd
import random
from datetime import datetime

def generate_live_signals():
    merchants = [
        {"id": 103, "name": "Global-Shop", "stage": "Headless", "tier": "Enterprise"},
        {"id": 205, "name": "Quick-Cart", "stage": "Hosted", "tier": "Basic"}
    ]
    
    # These represent the 'Next Up' queue
    tickets = [
        {
            "id": "T-001",
            "merchant_id": 103,
            "issue": "Webhook_Signature_Mismatch",
            "risk_score": 20, # Low
            "desc": "Orders are not appearing in my custom storefront dashboard."
        },
        {
            "id": "T-002",
            "merchant_id": 205,
            "issue": "Server_500_Timeout",
            "risk_score": 50, # Medium
            "desc": "I am getting a timeout error when trying to export my product CSV."
        },
        {
            "id": "T-003",
            "merchant_id": 103,
            "issue": "Critical_Database_Corruption",
            "risk_score": 90, # High
            "desc": "URGENT: Database sync failed, customer records are showing garbled text!"
        }
    ]
    
    return merchants, tickets

# Test function
if __name__ == "__main__":
    m, l, t = generate_live_signals()
    print(f"Signals Ingested: {len(m)} Merchants, {len(l)} Logs, {len(t)} Tickets")