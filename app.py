import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="B2B Intent Detector",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 B2B Buying Signal Detector")

INDUSTRIES   = ['SaaS','FinTech','HealthTech','E-commerce','Logistics',
                'EdTech','CyberSecurity','MarTech','HRTech','LegalTech']
COMPANY_SIZES = ['1-10','11-50','51-200','201-500','501-1000','1000+']
FUNDING_ROUNDS = {0:"None", 1:"Seed", 2:"Series A", 3:"Series B", 4:"Series C+"}

#  Sidebar 
st.sidebar.header("Company Signals")

company_name     = st.sidebar.text_input("Company Name", "Acme Corp")
industry         = st.sidebar.selectbox("Industry", INDUSTRIES)
company_size     = st.sidebar.selectbox("Company Size", COMPANY_SIZES)

st.sidebar.markdown("**📋 Hiring Signals**")
new_postings     = st.sidebar.slider("New job postings (30d)", 0, 50, 8)
hiring_sales     = st.sidebar.checkbox("Hiring Sales/Marketing", True)
hiring_eng       = st.sidebar.checkbox("Hiring Engineers", True)
posting_growth   = st.sidebar.slider("Job posting growth rate", -0.5, 2.0, 0.3, 0.05)

st.sidebar.markdown("**💰 Funding Signals**")
days_funded      = st.sidebar.slider("Days since last funding", 0, 730, 60)
funding_amt      = st.sidebar.number_input("Funding amount ($M)", 0.0, 500.0, 12.0)
funding_round    = st.sidebar.selectbox("Funding round", list(FUNDING_ROUNDS.keys()),
                                         format_func=lambda x: FUNDING_ROUNDS[x])

st.sidebar.markdown("**⚙️ Tech Signals**")
new_tools        = st.sidebar.slider("New tools added (90d)", 0, 15, 3)
using_competitor = st.sidebar.checkbox("Using competitor product", False)
stack_size       = st.sidebar.slider("Tech stack size", 5, 80, 25)

st.sidebar.markdown("**📈 Growth Signals**")
traffic_growth   = st.sidebar.slider("Web traffic growth (%)", -50, 100, 15)
linkedin_growth  = st.sidebar.slider("LinkedIn follower growth", -20, 50, 8)
news_mentions    = st.sidebar.slider("News mentions (30d)", 0, 20, 3)
announcement     = st.sidebar.checkbox("Recent announcement", False)

st.sidebar.markdown("**💌 Engagement**")
pricing_visit    = st.sidebar.checkbox("Visited pricing page", False)
email_score      = st.sidebar.slider("Email engagement score", 0.0, 1.0, 0.35, 0.05)
days_touch       = st.sidebar.slider("Days since last touch", 0, 365, 30)

score_btn = st.sidebar.button("Detect Buying Intent", type="primary",
                               use_container_width=True)

#  Main panel 
if score_btn:
    payload = {
        "company_name": company_name,
        "industry": industry,
        "company_size": company_size,
        "new_job_postings_30d": new_postings,
        "hiring_sales_marketing": int(hiring_sales),
        "hiring_engineers": int(hiring_eng),
        "job_posting_growth_rate": posting_growth,
        "days_since_funding": days_funded,
        "funding_amount_m": funding_amt,
        "funding_round": funding_round,
        "new_tools_added_90d": new_tools,
        "using_competitor": int(using_competitor),
        "tech_stack_size": stack_size,
        "web_traffic_growth_pct": traffic_growth,
        "linkedin_follower_growth": linkedin_growth,
        "news_mentions_30d": news_mentions,
        "has_recent_announcement": int(announcement),
        "visited_pricing_page": int(pricing_visit),
        "email_engagement_score": email_score,
        "days_since_last_touch": days_touch
    }

    with st.spinner("Analysing buying signals..."):
        try:
            resp   = requests.post(f"{API_URL}/score", json=payload)
            result = resp.json()
        except Exception as e:
            st.error(f"API connection failed: {e}")
            st.stop()

    # Tier colour
    tier_colors = {"Hot": "#e74c3c", "Warm": "#e67e22",
                   "Lukewarm": "#f1c40f", "Cold": "#95a5a6"}
    tier  = result["intent_tier"]
    color = tier_colors.get(tier, "#333")

    st.markdown(
        f"<div style='background:{color};padding:16px;border-radius:10px;"
        f"text-align:center;color:white;font-size:24px;font-weight:600'>"
        f"{result['decision']}  ·  {tier}</div>",
        unsafe_allow_html=True
    )
    st.markdown("")

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Company", result["company_name"])
    c2.metric("Intent Score", f"{result['intent_score']*100:.1f}%")
    c3.metric("Tier", tier)
    c4.metric("Action", "Immediate" if tier == "Hot" else "Scheduled")

    st.info(f"**Recommended Action:** {result['recommended_action']}")
    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Intent Score Gauge")
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(result['intent_score'] * 100, 1),
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 35],  "color": "#f0f0f0"},
                    {"range": [35, 55], "color": "#fff3cd"},
                    {"range": [55, 75], "color": "#ffd59e"},
                    {"range": [75, 100],"color": "#ffcccc"},
                ],
                "threshold": {"line": {"color": "black", "width": 3},
                              "value": 40}
            }
        ))
        fig.update_layout(height=280, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Signal Breakdown")

        buying = result["top_buying_signals"]
        missing = result["top_missing_signals"]

        if buying:
            st.markdown("**🟢 Active Buying Signals**")
            for s in buying:
                bar = "█" * int(s['strength'] * 100)
                st.markdown(f"`{s['signal']}` +{s['strength']}")

        if missing:
            st.markdown("**🔴 Weak / Missing Signals**")
            for s in missing:
                st.markdown(f"`{s['signal']}` gap: {s['gap']}")
