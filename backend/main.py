import os
from datetime import datetime
from backend.parser import LogParser
from backend.engine import DetectionEngine
from backend.ai_assistant import AIAssistant
from backend.database import SupabaseManager
from backend.telegram_bot import TelegramAlertBot

class BackendService:
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.parser = LogParser()
        self.engine = DetectionEngine()
        self.ai = AIAssistant()
        self.db = SupabaseManager()
        self.telegram = TelegramAlertBot()
        self.processed_log_ids = set()

        # Notify Telegram that system is online
        self.telegram.send_startup_message()

    def process_latest_logs(self):
        """
        Reads logs from Supabase (or local file if DB not connected),
        runs detection, sends Telegram alerts, and syncs to Supabase.
        """
        # 1. Fetch logs
        if self.db.client:
            raw_logs = self.db.get_latest_logs(limit=200)
            parsed_logs = [self.parser.parse_dict(l) for l in raw_logs]
        else:
            parsed_logs = self.parser.parse_file(self.log_path)

        if not parsed_logs:
            return {"status": "no_logs", "count": 0}

        # 2. Filter already processed logs
        new_logs = [l for l in parsed_logs if l.get('log_id') not in self.processed_log_ids]
        if not new_logs:
            return {"status": "success", "log_count": 0, "alerts": [], "ai_summary": "No new activity."}

        # 3. Run detection engine
        rule_alerts = self.engine.check_rules(new_logs)
        statistical_alerts, z_score = self.engine.check_statistical_anomaly(new_logs)
        all_alerts = rule_alerts + statistical_alerts

        # 4. Save anomaly score
        if self.db.client and z_score > 0:
            self.db.insert_anomaly_score({
                "score": z_score,
                "detected_at": datetime.now().isoformat()
            })

            # Populate login audit
            audit_batch = []
            for log in new_logs:
                if log['event_type'] == 'login_attempt':
                    audit_batch.append({
                        "ip_address": log['ip_address'],
                        "result": log['status'],
                        "timestamp": log['timestamp']
                    })
            if audit_batch:
                self.db.insert_login_audit_batch(audit_batch)

        # 5. AI summary
        summary = self.ai.summarize_logs(new_logs) if len(all_alerts) > 0 else "System stable. No critical threats found."

        # 6. Process alerts — classify, save, and send Telegram notifications
        critical_count = 0
        for alert in all_alerts:
            alert['ai_category'] = self.ai.classify_alert(alert['description'])

            # Save to Supabase
            if self.db.client:
                db_alert = {k: v for k, v in alert.items() if k != 'ai_category'}
                self.db.insert_alert(db_alert)

            # 🔔 Send Telegram alert
            self.telegram.send_alert(alert)

            if alert.get('severity') == 'Critical':
                critical_count += 1

        # 7. Send batch summary if there were alerts
        if all_alerts:
            self.telegram.send_summary(
                log_count=len(new_logs),
                alert_count=len(all_alerts),
                critical_count=critical_count
            )

        # Mark as processed
        for l in new_logs:
            if l.get('log_id'):
                self.processed_log_ids.add(l['log_id'])

        return {
            "status": "success",
            "log_count": len(new_logs),
            "alerts": all_alerts,
            "ai_summary": summary
        }

    def get_analytics_data(self):
        if self.db.client:
            return {
                "anomaly_scores": self.db.get_anomaly_scores(limit=100),
                "alerts": self.db.get_latest_alerts(limit=100)
            }
        return {"anomaly_scores": [], "alerts": []}

    def get_audit_data(self):
        if self.db.client:
            return self.db.get_login_audit(limit=200)
        return []

if __name__ == "__main__":
    LOG_PATH = "data/raw_logs.jsonl"
    service = BackendService(LOG_PATH)
    results = service.process_latest_logs()
    print(f"--- Process Batch Result (Logs: {results.get('log_count')}) ---")
    print(f"AI Summary: {results.get('ai_summary')}")
    print(f"Alerts Found: {len(results.get('alerts', []))}")
    for alert in results.get('alerts', []):
        print(f"  [{alert['severity']}] {alert['category']} ({alert['ai_category']}): {alert['description']}")
