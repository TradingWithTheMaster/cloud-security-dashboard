import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def clear_supabase_data():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: Supabase credentials not found.")
        return

    client: Client = create_client(url, key)
    
    tables = ["alerts", "login_audit", "anomaly_scores", "logs"]
    
    print("--- Starting Database Wipe ---")
    
    for table in tables:
        print(f"Clearing table: {table}...")
        try:
            # We use a broad filter to delete all rows
            # For UUID tables, we match everything. For log_id (bigint), we match id >= 0.
            if table == "logs":
                client.table(table).delete().gt("log_id", -1).execute()
            else:
                # UUID tables: Delete any row where id is not an empty UUID (matches everything)
                client.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print(f"Successfully cleared {table}")
        except Exception as e:
            print(f"Error clearing {table}: {e}")
            
    print("--- Database Wipe Complete ---")

if __name__ == "__main__":
    clear_supabase_data()
