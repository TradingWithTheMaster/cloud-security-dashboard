import uuid
import statistics
from datetime import datetime, timedelta
from typing import List, Dict

class DetectionEngine:
    def __init__(self):
        self.malicious_ips = ["45.33.22.11", "88.99.100.121"] # Placeholder "known bad" IPs
        
    def check_rules(self, logs: List[Dict]) -> List[Dict]:
        """
        Processes logs through predefined rules.
        """
        alerts = []
        
        # 1. Brute Force Rule (>5 failed login attempts from same IP in 5 mins)
        ip_failures = {}
        for log in logs:
            if log['event_type'] == 'login_attempt' and log['status'] == 'failed':
                ip = log['ip_address']
                if ip not in ip_failures:
                    ip_failures[ip] = []
                ip_failures[ip].append(datetime.fromisoformat(log['timestamp']))
        
        for ip, times in ip_failures.items():
            times.sort()
            # Sliding window check
            for i in range(len(times)):
                count = 0
                start_time = times[i]
                for j in range(i, len(times)):
                    if times[j] - start_time <= timedelta(minutes=5):
                        count += 1
                
                if count >= 5:
                    alerts.append(self._create_alert(
                        category="Brute Force",
                        severity="Critical",
                        description=f"Detected {count} failed login attempts from {ip} within 5 minutes.",
                        source_ip=ip,
                        linked_log_id=None # Multiple logs triggered this
                    ))
                    break # One alert per IP per batch for now
        
        # 2. Suspicious IP Rule
        for log in logs:
            if log['ip_address'] in self.malicious_ips:
                alerts.append(self._create_alert(
                    category="Suspicious IP",
                    severity="Warning",
                    description=f"Activity detected from known suspicious IP: {log['ip_address']}",
                    source_ip=log['ip_address'],
                    linked_log_id=log['log_id']
                ))

        # 3. System Anomaly (Simplified Rule: High volume of errors)
        error_logs = [log for log in logs if log['event_type'] == 'system_error']
        if len(error_logs) >= 3:
             alerts.append(self._create_alert(
                    category="Unusual Activity",
                    severity="Informational",
                    description=f"High frequency of system errors detected: {len(error_logs)} errors in current batch.",
                    source_ip="System",
                    linked_log_id=None
                ))

        return alerts

    def check_statistical_anomaly(self, logs: List[Dict]) -> (List[Dict], float):
        """
        Uses Z-score to detect unusual volume spikes.
        Returns (alerts, z_score)
        """
        if len(logs) < 10:
            return [], 0.0
            
        historical_failed_counts = [2, 3, 1, 4, 2, 2, 3, 1, 5, 2] 
        current_failed_count = len([l for l in logs if l['status'] == 'failed' or l['status'] == 'error'])
        
        mean_val = statistics.mean(historical_failed_counts)
        stdev_val = statistics.stdev(historical_failed_counts)
        
        if stdev_val == 0: return [], 0.0
        
        z_score = (current_failed_count - mean_val) / stdev_val
        
        alerts = []
        if z_score > 3:
            alerts.append(self._create_alert(
                category="Unusual Activity",
                severity="Warning",
                description=f"Statistical anomaly detected: Failed event count ({current_failed_count}) is {z_score:.2f} standard deviations above normal.",
                source_ip="Cluster",
                linked_log_id=None
            ))
        return alerts, z_score

    def _create_alert(self, category, severity, description, source_ip, linked_log_id):
        return {
            "id": str(uuid.uuid4()),
            "category": category,
            "severity": severity,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "source_ip": source_ip,
            "linked_log_id": linked_log_id
        }

# Quick test case
if __name__ == "__main__":
    test_logs = [
        {"log_id": 1, "ip_address": "1.1.1.1", "event_type": "login_attempt", "status": "failed", "timestamp": (datetime.now() - timedelta(minutes=1)).isoformat()},
        {"log_id": 2, "ip_address": "1.1.1.1", "event_type": "login_attempt", "status": "failed", "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat()},
        {"log_id": 3, "ip_address": "1.1.1.1", "event_type": "login_attempt", "status": "failed", "timestamp": (datetime.now() - timedelta(minutes=3)).isoformat()},
        {"log_id": 4, "ip_address": "1.1.1.1", "event_type": "login_attempt", "status": "failed", "timestamp": (datetime.now() - timedelta(minutes=4)).isoformat()},
        {"log_id": 5, "ip_address": "1.1.1.1", "event_type": "login_attempt", "status": "failed", "timestamp": datetime.now().isoformat()},
        {"log_id": 6, "ip_address": "45.33.22.11", "event_type": "file_access", "status": "success", "timestamp": datetime.now().isoformat()}
    ]
    engine = DetectionEngine()
    print("Rule Alerts:", engine.check_rules(test_logs))
