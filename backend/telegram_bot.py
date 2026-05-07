import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramAlertBot:
    """
    Sends real-time security alerts to Telegram when critical threats are detected.
    """
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.sent_alert_ids = set()  # Avoid duplicate alerts

    def send_message(self, message: str):
        """
        Sends a message to the configured Telegram chat.
        """
        if not self.token or not self.chat_id:
            print("[TELEGRAM] Bot not configured.")
            return False
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"[TELEGRAM ERROR] {e}")
            return False

    def send_alert(self, alert: dict):
        """
        Formats and sends a security alert to Telegram.
        Only sends Critical and Warning alerts, no duplicates.
        """
        alert_id = alert.get("id")
        severity = alert.get("severity", "")

        # Only send Critical and Warning alerts
        if severity not in ["Critical", "Warning"]:
            return

        # Skip duplicates
        if alert_id and alert_id in self.sent_alert_ids:
            return

        # Format the message
        emoji = "🚨" if severity == "Critical" else "⚠️"
        category = alert.get("category", "Unknown")
        description = alert.get("description", "No details.")
        source_ip = alert.get("source_ip", "Unknown")
        timestamp = alert.get("timestamp", "")[:19].replace("T", " ")

        message = (
            f"{emoji} <b>SECURITY ALERT — {severity.upper()}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>Category:</b> {category}\n"
            f"🌐 <b>Source IP:</b> <code>{source_ip}</code>\n"
            f"🕒 <b>Time:</b> {timestamp}\n"
            f"📝 <b>Details:</b> {description}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🖥️ <i>Cloud Security Monitor — OSTIM Tech University</i>"
        )

        success = self.send_message(message)
        if success and alert_id:
            self.sent_alert_ids.add(alert_id)
            print(f"[TELEGRAM] Alert sent: {category} from {source_ip}")

    def send_startup_message(self):
        """
        Sends a startup notification when the system comes online.
        """
        message = (
            "🛡️ <b>CLOUD SECURITY MONITOR — ONLINE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✅ System is now active and monitoring logs.\n"
            "🔍 Real-time threat detection is running.\n"
            "🤖 Gemini AI analysis is enabled.\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📡 You will receive alerts for Critical and Warning threats.\n"
            "<i>Cloud Security Monitor — OSTIM Tech University</i>"
        )
        self.send_message(message)

    def send_summary(self, log_count: int, alert_count: int, critical_count: int):
        """
        Sends a batch summary after processing logs.
        """
        if alert_count == 0:
            return
        message = (
            f"📊 <b>BATCH PROCESSING SUMMARY</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 Logs Processed: <b>{log_count}</b>\n"
            f"🚨 Critical Alerts: <b>{critical_count}</b>\n"
            f"⚠️ Total Alerts: <b>{alert_count}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Check your dashboard for full details.</i>"
        )
        self.send_message(message)
