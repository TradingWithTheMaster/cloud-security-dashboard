import json
import time
import random
from datetime import datetime
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import SupabaseManager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "data", "raw_logs.jsonl")

# Initialize DB Manager
db_manager = SupabaseManager()

EVENT_TYPES = ["login_attempt", "file_access", "system_error"]
STATUSES = {
    "login_attempt": ["success", "failed"],
    "file_access": ["success", "failed"],
    "system_error": ["error"]
}

IP_ADDRESSES = [
    "192.168.1.10", "192.168.1.11", "10.0.0.5", "172.16.254.1",
    "45.33.22.11", "88.99.100.121" 
]

def generate_log(log_id):
    event_type = random.choice(EVENT_TYPES)
    ip = random.choice(IP_ADDRESSES)
    status = random.choice(STATUSES[event_type])
    timestamp = datetime.now().isoformat()

    log_entry = {
        "ip_address": ip,
        "event_type": event_type,
        "status": status,
        "timestamp": timestamp
    }
    return log_entry

def main():
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))
        
    print(f"Starting log simulator... Writing to {LOG_FILE}")
    log_id = 1
    try:
        while True:
            log = generate_log(log_id)
            
            # 1. Write to local file (as backup)
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(log) + "\n")
            
            # 2. Sync to Supabase
            if db_manager.client:
                try:
                    db_manager.insert_log(log)
                    print(f"[SIMULATOR] Synced to Supabase: {log['event_type']}")
                except Exception as e:
                    print(f"[ERROR] Failed to sync to Supabase: {e}")
            
            print(f"[SIMULATOR] Generated: {log}")
            
            log_id += 1
            time.sleep(random.uniform(1.0, 5.0))
    except KeyboardInterrupt:
        print("\nSimulator stopped.")

if __name__ == "__main__":
    main()
