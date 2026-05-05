import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.main import BackendService

# --- Page Config ---
st.set_page_config(page_title="Cloud Security Monitor", layout="wide", page_icon="🛡️")

# --- Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif;
    }

    .main {
        background: #050d1a;
        color: #c8d8e8;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #050d1a 0%, #0a1628 50%, #050d1a 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #070f20 0%, #0d1a30 100%) !important;
        border-right: 1px solid #1a3a5c !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0a1628 0%, #0d2040 100%);
        border: 1px solid #1a3a5c;
        border-radius: 12px;
        padding: 20px !important;
        box-shadow: 0 0 20px rgba(0, 150, 255, 0.08), inset 0 1px 0 rgba(255,255,255,0.05);
        position: relative;
        overflow: hidden;
    }

    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00aaff, transparent);
    }

    [data-testid="stMetricValue"] {
        color: #00cfff !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 20px rgba(0, 207, 255, 0.5) !important;
    }

    [data-testid="stMetricLabel"] {
        color: #5a8ab0 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }

    /* Critical metric - red glow */
    .critical-metric [data-testid="stMetricValue"] {
        color: #ff4444 !important;
        text-shadow: 0 0 20px rgba(255, 68, 68, 0.5) !important;
    }

    h1 {
        font-family: 'Share Tech Mono', monospace !important;
        color: #00cfff !important;
        font-size: 1.8rem !important;
        letter-spacing: 3px !important;
        text-shadow: 0 0 30px rgba(0, 207, 255, 0.4) !important;
        border-bottom: 1px solid #1a3a5c;
        padding-bottom: 12px;
        margin-bottom: 20px !important;
    }

    h2, h3 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #7ab8d4 !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        font-size: 0.9rem !important;
    }

    /* Sidebar */
    .sidebar-title {
        font-family: 'Share Tech Mono', monospace;
        color: #00cfff;
        font-size: 1rem;
        letter-spacing: 2px;
        text-shadow: 0 0 15px rgba(0, 207, 255, 0.4);
        padding: 10px 0;
        border-bottom: 1px solid #1a3a5c;
        margin-bottom: 15px;
    }

    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 255, 100, 0.1);
        border: 1px solid rgba(0, 255, 100, 0.3);
        color: #00ff64;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 2px;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: 'Share Tech Mono', monospace;
    }

    .pulse-dot {
        width: 6px; height: 6px;
        background: #00ff64;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 1.5s infinite;
        box-shadow: 0 0 6px #00ff64;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* Alert box */
    .ai-insight-box {
        background: linear-gradient(135deg, #030d20 0%, #071828 100%);
        border: 1px solid #1a4060;
        border-left: 3px solid #00aaff;
        border-radius: 8px;
        padding: 18px 22px;
        font-size: 0.9rem;
        line-height: 1.7;
        color: #8ab8d4;
        font-family: 'Rajdhani', sans-serif;
        box-shadow: 0 0 30px rgba(0, 100, 200, 0.08);
    }

    /* Section headers */
    .section-header {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.7rem;
        color: #2a6090;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin: 20px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #0d2a42;
    }

    /* Severity badges */
    .badge-critical {
        background: rgba(255, 50, 50, 0.15);
        color: #ff5555;
        border: 1px solid rgba(255, 50, 50, 0.4);
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        font-family: 'Share Tech Mono', monospace;
    }

    .badge-warning {
        background: rgba(255, 170, 0, 0.15);
        color: #ffaa00;
        border: 1px solid rgba(255, 170, 0, 0.4);
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        font-family: 'Share Tech Mono', monospace;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #1a3a5c !important;
        border-radius: 8px !important;
    }

    /* Radio buttons */
    .stRadio label {
        color: #5a8ab0 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        font-size: 0.85rem !important;
    }

    .stRadio [data-checked="true"] label {
        color: #00cfff !important;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #0a2040, #0d3060) !important;
        border: 1px solid #1a4a7a !important;
        color: #00cfff !important;
        font-family: 'Share Tech Mono', monospace !important;
        letter-spacing: 2px !important;
        font-size: 0.75rem !important;
        border-radius: 6px !important;
        transition: all 0.2s !important;
    }

    .stButton button:hover {
        border-color: #00aaff !important;
        box-shadow: 0 0 15px rgba(0, 170, 255, 0.3) !important;
    }

    /* Info/warning boxes */
    .stInfo, .stWarning {
        background: #071828 !important;
        border-color: #1a4060 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Divider */
    hr {
        border-color: #0d2a42 !important;
        margin: 15px 0 !important;
    }

    /* Scanline overlay effect */
    [data-testid="stAppViewContainer"]::after {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 0, 0, 0.03) 2px,
            rgba(0, 0, 0, 0.03) 4px
        );
        pointer-events: none;
        z-index: 9999;
    }
    </style>
""", unsafe_allow_html=True)

# --- Backend Init ---
if 'backend' not in st.session_state:
    LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/raw_logs.jsonl"))
    st.session_state.backend = BackendService(LOG_PATH)

# Auto-refresh every 30s
st_autorefresh(interval=30 * 1000, key="data_refresh")

# --- Cached data ---
@st.cache_data(ttl=120)
def get_processed_data():
    return st.session_state.backend.process_latest_logs()

@st.cache_data(ttl=120)
def get_logs_cached(limit=100):
    if st.session_state.backend.db.client:
        return st.session_state.backend.db.get_latest_logs(limit=limit)
    return st.session_state.backend.parser.parse_file(st.session_state.backend.log_path)

@st.cache_data(ttl=120)
def get_alerts_cached(limit=100):
    return st.session_state.backend.db.get_latest_alerts(limit=limit)

@st.cache_data(ttl=120)
def get_analytics_cached():
    return st.session_state.backend.get_analytics_data()

@st.cache_data(ttl=120)
def get_audit_cached():
    return st.session_state.backend.get_audit_data()

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">⬡ CLOUD SECURITY<br>MONITOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-online"><span class="pulse-dot"></span> SYSTEM ONLINE</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-header">// Navigation</div>', unsafe_allow_html=True)
    page = st.radio("",
        ["📊 Dashboard", "📋 Log Browser", "🚨 Alerts", "📈 Analytics", "🔑 Login Audit", "👤 User Management"],
        label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">// System</div>', unsafe_allow_html=True)
    st.markdown("**ADMINISTRATOR**", unsafe_allow_html=True)
    st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')}")

    st.divider()
    if st.button("⟳ FORCE REFRESH"):
        st.cache_data.clear()
        st.rerun()

    st.markdown('<br><span style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;color:#1a4060;">v1.2.5 // OSTIM TECH UNIV.</span>', unsafe_allow_html=True)

# =====================
# PAGE: DASHBOARD
# =====================
if page == "📊 Dashboard":
    st.markdown("# 🛡️ SECURITY DASHBOARD")

    data = get_processed_data()

    if data["status"] == "no_logs":
        st.warning("⚠️ No logs found. Please start the log simulator.")
    else:
        df_alerts = pd.DataFrame(data["alerts"]) if data["alerts"] else pd.DataFrame(get_alerts_cached())
        logs = get_logs_cached(limit=1000)
        df_logs = pd.DataFrame(logs)

        # --- Metrics Row ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL LOGS", len(df_logs))
        m2.metric("CRITICAL ALERTS", len(df_alerts[df_alerts['severity'] == 'Critical']) if not df_alerts.empty else 0)
        m3.metric("WARNINGS", len(df_alerts[df_alerts['severity'] == 'Warning']) if not df_alerts.empty else 0)
        m4.metric("ACTIVE THREATS", len(df_alerts))

        st.divider()

        # --- AI Insight ---
        st.markdown('<div class="section-header">// AI Security Insight — Powered by Gemini</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-insight-box">{data["ai_summary"]}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Charts Row ---
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="section-header">// Login Success vs Failure</div>', unsafe_allow_html=True)
            if not df_logs.empty and 'status' in df_logs.columns:
                login_df = df_logs[df_logs['event_type'] == 'login_attempt']
                fig = px.pie(
                    login_df, names='status', hole=0.55,
                    color_discrete_map={'success': '#00ff64', 'failed': '#ff4444'}
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#7ab8d4', family='Rajdhani'),
                    legend=dict(font=dict(color='#7ab8d4')),
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                fig.update_traces(textfont_color='white')
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="section-header">// Top Suspicious IPs</div>', unsafe_allow_html=True)
            if not df_alerts.empty and 'source_ip' in df_alerts.columns:
                ip_counts = df_alerts['source_ip'].value_counts().reset_index()
                ip_counts.columns = ['IP Address', 'Alert Count']
                fig2 = px.bar(
                    ip_counts, x='IP Address', y='Alert Count',
                    color='Alert Count',
                    color_continuous_scale=[[0, '#0a3060'], [0.5, '#0066cc'], [1, '#ff3333']]
                )
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(5,13,26,0.8)',
                    font=dict(color='#7ab8d4', family='Rajdhani'),
                    coloraxis_showscale=False,
                    xaxis=dict(gridcolor='#0d2a42', tickfont=dict(color='#5a8ab0')),
                    yaxis=dict(gridcolor='#0d2a42', tickfont=dict(color='#5a8ab0')),
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                fig2.update_traces(marker_line_color='rgba(0,150,255,0.3)', marker_line_width=1)
                st.plotly_chart(fig2, use_container_width=True)

        # --- Event Type Breakdown ---
        st.markdown('<div class="section-header">// Event Type Breakdown</div>', unsafe_allow_html=True)
        if not df_logs.empty and 'event_type' in df_logs.columns:
            event_counts = df_logs['event_type'].value_counts().reset_index()
            event_counts.columns = ['Event Type', 'Count']
            fig3 = px.bar(
                event_counts, x='Count', y='Event Type', orientation='h',
                color='Count',
                color_continuous_scale=[[0, '#0a3060'], [1, '#00aaff']]
            )
            fig3.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(5,13,26,0.8)',
                font=dict(color='#7ab8d4', family='Rajdhani'),
                coloraxis_showscale=False,
                xaxis=dict(gridcolor='#0d2a42', tickfont=dict(color='#5a8ab0')),
                yaxis=dict(gridcolor='#0d2a42', tickfont=dict(color='#5a8ab0')),
                margin=dict(t=10, b=20, l=20, r=20),
                height=220
            )
            st.plotly_chart(fig3, use_container_width=True)

        # --- Recent Alerts Table ---
        if not df_alerts.empty:
            st.markdown('<div class="section-header">// Recent Alerts</div>', unsafe_allow_html=True)
            display_cols = [c for c in ['timestamp', 'severity', 'category', 'description', 'source_ip'] if c in df_alerts.columns]
            st.dataframe(
                df_alerts[display_cols].head(10),
                use_container_width=True,
                hide_index=True
            )

# =====================
# PAGE: LOG BROWSER
# =====================
elif page == "📋 Log Browser":
    st.markdown("# 📋 LOG BROWSER")

    with st.expander("⚙️ FILTERS", expanded=True):
        f1, f2, f3 = st.columns(3)
        event_filter = f1.text_input("Event Type", placeholder="e.g. login_attempt")
        max_records = f2.slider("Max Records", 10, 1000, 100)
        search_query = f3.text_input("Search", placeholder="e.g. 192.168.1.1")

    raw_logs = get_logs_cached(limit=max_records)
    df = pd.DataFrame(raw_logs)

    t1, t2, t3, t4 = st.columns(4)
    if not df.empty:
        if event_filter:
            df = df[df['event_type'].str.contains(event_filter, case=False, na=False)]
        if search_query:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        failed = len(df[df['status'] == 'failed']) if 'status' in df.columns else 0
        success = len(df[df['status'] == 'success']) if 'status' in df.columns else 0

        t1.metric("TOTAL SHOWN", len(df))
        t2.metric("FAILED", failed)
        t3.metric("SUCCESS", success)
        t4.metric("OTHER", len(df) - failed - success)

        st.divider()
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        t1.metric("TOTAL SHOWN", "0")
        t2.metric("FAILED", "0")
        t3.metric("SUCCESS", "0")
        t4.metric("OTHER", "0")
        st.divider()
        st.info("No logs match the current filters.")

# =====================
# PAGE: ALERTS
# =====================
elif page == "🚨 Alerts":
    st.markdown("# 🚨 SECURITY ALERTS")

    alerts = get_alerts_cached(limit=100)
    if alerts:
        df_a = pd.DataFrame(alerts)

        # Summary row
        a1, a2, a3 = st.columns(3)
        a1.metric("TOTAL ALERTS", len(df_a))
        a2.metric("CRITICAL", len(df_a[df_a['severity'] == 'Critical']) if 'severity' in df_a.columns else 0)
        a3.metric("WARNINGS", len(df_a[df_a['severity'] == 'Warning']) if 'severity' in df_a.columns else 0)

        st.divider()

        # Severity filter
        sev_filter = st.selectbox("Filter by Severity", ["All", "Critical", "Warning", "Informational"])
        if sev_filter != "All" and 'severity' in df_a.columns:
            df_a = df_a[df_a['severity'] == sev_filter]

        st.dataframe(df_a, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No alerts found — system is stable.")

# =====================
# PAGE: ANALYTICS
# =====================
elif page == "📈 Analytics":
    st.markdown("# 📈 SECURITY ANALYTICS")

    analytics = get_analytics_cached()

    if analytics["anomaly_scores"]:
        df_scores = pd.DataFrame(analytics["anomaly_scores"])
        st.markdown('<div class="section-header">// Statistical Anomaly Z-Score Trend</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_scores['detected_at'], y=df_scores['score'],
            mode='lines+markers',
            line=dict(color='#00aaff', width=2),
            marker=dict(color='#00cfff', size=6, symbol='diamond'),
            fill='tozeroy',
            fillcolor='rgba(0, 150, 255, 0.08)',
            name='Z-Score'
        ))
        fig.add_hline(y=3, line_dash="dash", line_color="#ff4444",
                      annotation_text="CRITICAL THRESHOLD", annotation_font_color="#ff4444")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(5,13,26,0.8)',
            font=dict(color='#7ab8d4', family='Rajdhani'),
            xaxis=dict(gridcolor='#0d2a42', tickfont=dict(color='#5a8ab0')),
            yaxis=dict(gridcolor='#0d2a42', tickfont=dict(color='#5a8ab0')),
            margin=dict(t=20, b=20),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No anomaly score data yet. Let the simulator run for a while.")

    # Alert category breakdown
    alerts = get_alerts_cached(limit=200)
    if alerts:
        df_a = pd.DataFrame(alerts)
        st.markdown('<div class="section-header">// Alert Category Distribution</div>', unsafe_allow_html=True)
        if 'category' in df_a.columns:
            cat_counts = df_a['category'].value_counts().reset_index()
            cat_counts.columns = ['Category', 'Count']
            fig2 = px.pie(cat_counts, names='Category', values='Count', hole=0.5,
                         color_discrete_sequence=['#ff4444', '#ffaa00', '#00aaff', '#00ff64'])
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#7ab8d4', family='Rajdhani'),
                legend=dict(font=dict(color='#7ab8d4')),
                margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

# =====================
# PAGE: LOGIN AUDIT
# =====================
elif page == "🔑 Login Audit":
    st.markdown("# 🔑 LOGIN AUDIT TRAIL")

    audit = get_audit_cached()
    if audit:
        df_audit = pd.DataFrame(audit)
        if 'result' in df_audit.columns:
            df_audit = df_audit.rename(columns={'result': 'status'})

        a1, a2, a3 = st.columns(3)
        a1.metric("TOTAL LOGINS", len(df_audit))
        if 'status' in df_audit.columns:
            a2.metric("FAILED", len(df_audit[df_audit['status'] == 'failed']))
            a3.metric("SUCCESS", len(df_audit[df_audit['status'] == 'success']))

        st.divider()
        st.dataframe(df_audit, use_container_width=True, hide_index=True)
    else:
        st.info("No login audit records found yet.")

# =====================
# PAGE: USER MANAGEMENT
# =====================
elif page == "👤 User Management":
    st.markdown("# 👤 USER MANAGEMENT")
    st.markdown('<div class="ai-insight-box">🔧 User access control and role management module is planned for v1.3. This feature will include role-based access control (RBAC), user activity tracking, and permission management.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL USERS", "4")
    col2.metric("ACTIVE ROLES", "2")
    col3.metric("ADMIN ACCOUNTS", "1")
