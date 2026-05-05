import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()

class SupabaseManager:
    """
    Handles all interactions with the Supabase database.
    """
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            print("[WARNING] Supabase credentials not found in environment variables.")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)

    def insert_log(self, log_data: dict):
        """
        Inserts a single log into the 'logs' table.
        """
        if not self.client:
            return None
        return self.client.table("logs").insert(log_data).execute()

    def insert_alert(self, alert_data: dict):
        """
        Inserts a generated alert into the 'alerts' table.
        """
        if not self.client:
            return None
        return self.client.table("alerts").insert(alert_data).execute()

    def get_latest_logs(self, limit=100):
        """
        Fetches the latest logs from the 'logs' table.
        """
        if not self.client:
            return []
        response = self.client.table("logs").select("*").order("timestamp", desc=True).limit(limit).execute()
        return response.data

    def get_latest_alerts(self, limit=50):
        """
        Fetches the latest alerts from the 'alerts' table.
        """
        if not self.client:
            return []
        response = self.client.table("alerts").select("*").order("timestamp", desc=True).limit(limit).execute()
        return response.data

    def get_anomaly_scores(self, limit=100):
        """
        Fetches the latest anomaly scores.
        """
        if not self.client:
            return []
        response = self.client.table("anomaly_scores").select("*").order("detected_at", desc=True).limit(limit).execute()
        return response.data

    def get_login_audit(self, limit=100):
        """
        Fetches the latest login audit logs.
        """
        if not self.client:
            return []
        response = self.client.table("login_audit").select("*").order("timestamp", desc=True).limit(limit).execute()
        return response.data

    def insert_anomaly_score(self, score_data):
        """
        Inserts a new anomaly score into Supabase.
        """
        if not self.client:
            return False
        self.client.table("anomaly_scores").insert(score_data).execute()
        return True

    def insert_login_audit(self, audit_data):
        """
        Inserts a new login audit record into Supabase.
        """
        if not self.client:
            return False
        self.client.table("login_audit").insert(audit_data).execute()
        return True

    def insert_login_audit_batch(self, audit_data_list):
        """
        Inserts multiple login audit records in a single request.
        """
        if not self.client or not audit_data_list:
            return False
        self.client.table("login_audit").insert(audit_data_list).execute()
        return True
