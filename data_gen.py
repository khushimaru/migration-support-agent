import pandas as pd
import random
from datetime import datetime

def generate_live_signals():
    # 1. Simulate Merchant Migration Status
    # Some are on the old 'Hosted' system, some on the new 'Headless' one.
    merchants = [
        {"id": 101, "name": "GlobalShop", "stage": "Headless", "progress": 100},
        {"id": 102, "name": "TechFlow", "stage": "Hosted", "progress": 0},
        {"id": 103, "name": "QuickCart", "stage": "Headless", "progress": 45} # In the middle of moving!
    ]
    
    # 2. Simulate System Logs (The 'Invisible' Errors)
    # We'll create a "Migration Error" pattern here.
    logs = [
        {"timestamp": str(datetime.now()), "merchant_id": 103, "level": "ERROR", "event": "Webhook_Signature_Mismatch"},
        {"timestamp": str(datetime.now()), "merchant_id": 101, "level": "INFO", "event": "Successful_Checkout"}
    ]
    
    # 3. Simulate Incoming Support Tickets (The 'Human' Signals)
    tickets = [
        {"id": "TKT-501", "merchant_id": 103, "text": "Help! My checkout is failing after I updated to the new API.", "priority": "High"}
    ]
    
    return merchants, logs, tickets

# Test function
if __name__ == "__main__":
    m, l, t = generate_live_signals()
    print(f"Signals Ingested: {len(m)} Merchants, {len(l)} Logs, {len(t)} Tickets")