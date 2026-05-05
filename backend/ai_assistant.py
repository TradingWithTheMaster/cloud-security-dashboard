import os
import json
import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class AIAssistant:
    """
    AI-assisted logs analysis and alert classification using Google Gemini.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-lite-latest')
        else:
            self.model = None
            print("[WARNING] Google API Key not found. AI features will use mock logic.")

    def summarize_logs(self, logs: List[Dict]) -> str:
        """
        Summarizes a batch of logs using Gemini.
        """
        if not logs:
            return "No logs to summarize."
            
        if not self.model:
            return self._mock_summary(logs)

        try:
            prompt = f"Analyze these security logs and provide a concise summary of potential threats:\n{json.dumps(logs[:20])}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                return f"[Quota Reached] {self._mock_summary(logs)} (AI resting...)"
            return f"AI Summary (Error): {str(e)}"

    def classify_alert(self, description: str) -> str:
        """
        Classifies an alert description using Gemini.
        """
        if not self.model:
            return self._mock_classification(description)

        try:
            prompt = f"Classify this security alert description into a single short category (e.g. Brute Force, Suspicious Activity, System Error):\n{description}"
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "Unclassified (AI Error)"

    def _mock_summary(self, logs: List[Dict]) -> str:
        log_count = len(logs)
        failed_count = len([l for l in logs if l['status'] in ['failed', 'error']])
        return f"Batch Summary (Simulated): {log_count} events, {failed_count} failures detected."

    def _mock_classification(self, description: str) -> str:
        if "failed login" in description.lower(): return "Brute Force"
        return "General Alert"

# Test
if __name__ == "__main__":
    assistant = AIAssistant()
    print(assistant.summarize_logs([{"event": "test"}]))
