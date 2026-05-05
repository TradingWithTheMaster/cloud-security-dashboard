import json
import os

class LogParser:
    """
    Dedicated module to extract IP address, event type, status, and timestamp from raw logs.
    """
    
    @staticmethod
    def parse_line(line: str):
        """
        Parses a single line of raw JSON log.
        """
        try:
            data = json.loads(line.strip())
            return {
                "log_id": data.get("log_id"),
                "ip_address": data.get("ip_address"),
                "event_type": data.get("event_type"),
                "status": data.get("status"),
                "timestamp": data.get("timestamp")
            }
        except json.JSONDecodeError:
            return None

    @staticmethod
    def parse_dict(data: dict):
        """
        Validates and structure a log dictionary from Supabase.
        """
        return {
            "log_id": data.get("log_id"),
            "ip_address": data.get("ip_address"),
            "event_type": data.get("event_type"),
            "status": data.get("status"),
            "timestamp": data.get("timestamp")
        }

    @staticmethod
    def parse_file(file_path: str):
        """
        Parses an entire file of JSONL logs.
        """
        parsed_logs = []
        if not os.path.exists(file_path):
            return parsed_logs
            
        with open(file_path, "r") as f:
            for line in f:
                parsed = LogParser.parse_line(line)
                if parsed:
                    parsed_logs.append(parsed)
        return parsed_logs

# Quick test if run directly
if __name__ == "__main__":
    test_line = '{"log_id": 1, "ip_address": "192.168.1.1", "event_type": "login_attempt", "status": "failed", "timestamp": "2026-03-14T23:00:00"}'
    print(f"Test Parse: {LogParser.parse_line(test_line)}")
