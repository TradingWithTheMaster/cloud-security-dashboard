# 🛡️ CloudGuard Cloud Security Monitoring Dashboard

A real-time cloud security monitoring system we built as our Computer Engineering 
graduation project at **OSTİM Technical University**.

The idea came from a simple problem: tools like Splunk and IBM QRadar are great 
but cost thousands of dollars a month. We wanted to build something that actually 
works, costs nothing, and any small company could set up in minutes.

## 🚀 What it does

- Real-time security dashboard built with Streamlit
- Detects brute force attacks, suspicious IPs, and system anomalies automatically
- Uses Google Gemini AI to summarize threats in plain English
- Sends instant Telegram alerts when something suspicious is detected
- Z-score statistical analysis to catch unusual activity patterns
- Everything stored in Supabase (PostgreSQL) in the cloud

## 👥 Team

| Name | Role |
|------|------|
| Khalid Abdi Mohamed | Project Leader & Dashboard Development |
| Mohamed Abshir Jama | Backend & Database |
| Rahma Ahmed Hussien | Documentation & Design |

**Advisor:** Dr. Metin Balcı

## 🛠️ Tech Stack

- Python, Streamlit
- Supabase (PostgreSQL)
- Google Gemini AI
- Telegram Bot API
- Plotly, Pandas

## ⚙️ Getting Started

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys (see `.env.example`)
4. Start the log simulator: `python simulator/log_generator.py`
5. Launch the dashboard: `python -m streamlit run dashboard/app.py`

## 📄 Paper

Our research paper is published and available here:
- **Zenodo (DOI):** https://doi.org/10.5281/zenodo.20244898

## 🏫 OSTİM Technical University — Computer Engineering 2026
