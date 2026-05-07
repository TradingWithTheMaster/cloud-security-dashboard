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
        self.last_ai_summary = "🤖 AI Security Monitor active. Gemini analysis ready for new threats."
        self.startup_done = False
        self._preload_existing_ids()

    def _preload_existing_ids(self):
        try:
            if self.db.client:
                existing_logs = self.db.get_latest_logs(limit=200)
                for log in existing_logs:
                    if log.get('log_id'):
                        self.processed_log_ids.add(log['log_id'])

                existing_alerts = self.db.get_latest_alerts(limit=100)
                for alert in existing_alerts:
                    if alert.get('id'):
                        self.telegram.sent_alert_ids.add(alert['id'])

                print(f"[INIT] Pre-loaded {len(self.processed_log_ids)} logs, {len(self.telegram.sent_alert_ids)} alerts.")

            startup_flag = os.path.join(os.path.dirname(__file__), '.startup_sent')
            if not os.path.exists(startup_flag):
                self.telegram.send_startup_message()
                open(startup_flag, 'w').write('1')

        except Exception as e:
            print(f"[INIT ERROR] {e}")
        finally:
            self.startup_done = True

    def process_latest_logs(self):
        try:
            if self.db.client:
                raw_logs = self.db.get_latest_logs(limit=200)
                parsed_logs = [self.parser.parse_dict(l) for l in raw_logs]
            else:
                parsed_logs = self.parser.parse_file(self.log_path)

            if not parsed_logs:
                return {
                    "status": "no_logs",
                    "count": 0,
                    "alerts": [],
                    "ai_summary": self.last_ai_summary
                }

            new_logs = [l for l in parsed_logs if l.get('log_id') not in self.processed_log_ids]

            if not new_logs:
                existing_alerts = self.db.get_latest_alerts(limit=50) if self.db.client else []
                return {
                    "status": "success",
                    "log_count": 0,
                    "alerts": existing_alerts,
                    "ai_summary": self.last_ai_summary
                }

            print(f"[PROCESS] {len(new_logs)} new logs detected.")

            rule_alerts = self.engine.check_rules(new_logs)
            statistical_alerts, z_score = self.engine.check_statistical_anomaly(new_logs)
            all_alerts = rule_alerts + statistical_alerts

            if self.db.client and z_score > 0:
                self.db.insert_anomaly_score({
                    "score": z_score,
                    "detected_at": datetime.now().isoformat()
                })

            if self.db.client:
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

            # AI disabled for stability — enable after presentation
            # if all_alerts:
            #     try:
            #         self.last_ai_summary = self.ai.summarize_logs(new_logs[:10])
            #     except Exception:
            #         pass

            critical_count = 0
            saved_alerts = []
            for alert in all_alerts:
                alert['ai_category'] = alert.get('category', 'Unknown')

                if self.db.client:
                    db_alert = {k: v for k, v in alert.items() if k != 'ai_category'}
                    self.db.insert_alert(db_alert)

                self.telegram.send_alert(alert)

                if alert.get('severity') == 'Critical':
                    critical_count += 1
                saved_alerts.append(alert)

            if critical_count > 0:
                self.telegram.send_summary(
                    log_count=len(new_logs),
                    alert_count=len(all_alerts),
                    critical_count=critical_count
                )

            for l in new_logs:
                if l.get('log_id'):
                    self.processed_log_ids.add(l['log_id'])

            all_display_alerts = self.db.get_latest_alerts(limit=50) if self.db.client else saved_alerts

            return {
                "status": "success",
                "log_count": len(new_logs),
                "alerts": all_display_alerts,
                "ai_summary": self.last_ai_summary
            }

        except Exception as e:
            print(f"[PROCESS ERROR] {e}")
            return {
                "status": "error",
                "log_count": 0,
                "alerts": [],
                "ai_summary": self.last_ai_summary
            }

    def get_analytics_data(self):
        try:
            if self.db.client:
                return {
                    "anomaly_scores": self.db.get_anomaly_scores(limit=100),
                    "alerts": self.db.get_latest_alerts(limit=100)
                }
        except Exception as e:
            print(f"[ANALYTICS ERROR] {e}")
        return {"anomaly_scores": [], "alerts": []}

    def get_audit_data(self):
        try:
            if self.db.client:
                return self.db.get_login_audit(limit=200)
        except Exception as e:
            print(f"[AUDIT ERROR] {e}")
        return []