import json
import time
from datetime import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import SupabaseManager

# Initialize DB Manager
db_manager = SupabaseManager()

def fire_log(ip, event, status):
    log = {
        "ip_address": ip,
        "event_type": event,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    if db_manager.client:
        try:
            db_manager.insert_log(log)
            print(f"[ATTACK] Synced to Supabase: {event} from {ip}")
        except Exception as e:
            print(f"[ERROR] Failed to sync attack log: {e}")
    else:
        print(f"[LOCAL ONLY] Fired: {log}")

def simulate_brute_force(target_ip):
    print(f"--- Simulating Brute Force from {target_ip} ---")
    for _ in range(7):
        fire_log(target_ip, "login_attempt", "failed")
        time.sleep(0.5)

def simulate_system_errors():
    print("--- Simulating System Errors ---")
    for _ in range(5):
        fire_log("127.0.0.1", "system_error", "error")
        time.sleep(0.5)

if __name__ == "__main__":
    simulate_brute_force("1.2.3.4")
    simulate_system_errors()
    print("Attack simulation complete. Check your Supabase logs and dashboard.")
