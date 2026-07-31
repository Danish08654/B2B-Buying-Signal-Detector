import streamlit as st
import json
from groq import Groq
import plotly.graph_objects as go

st.set_page_config(page_title="IntentPulse", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*, body { font-family: 'Inter', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .block-container
    { background: #f8fafc !important; }
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div
    { background: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
#MainMenu, footer, header { visibility: hidden; }
p, div, span, label { color: #1e293b !important; }
h1, h2, h3 { color: #0f172a !important; }

.stTextInput input { background: #fff !important; color: #0f172a !important; border: 1.5px solid #cbd5e1 !important; border-radius: 8px !important; }
.stSelectbox > div > div { background: #fff !important; border: 1.5px solid #cbd5e1 !important; border-radius: 8px !important; color: #0f172a !important; }
.stNumberInput input { background: #fff !important; color: #0f172a !important; border: 1.5px solid #cbd5e1 !important; border-radius: 8px !important; }
.stSlider label, .stCheckbox span, .stSelectbox label, .stTextInput label, .stNumberInput label { color: #374151 !important; font-weight: 500 !important; font-size: 0.85rem !important; }
.stButton > button { background: #2563eb !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 11px !important; }
.stButton > button:hover { background: #1d4ed8 !important; }
hr { border-color: #e2e8f0 !important; }

.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
.metric-lbl { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: .09em; color: #64748b; margin-bottom: 5px; }
.metric-val { font-size: 1.7rem; font-weight: 700; color: #0f172a; }
.tier-banner { border-radius: 10px; padding: 16px 24px; text-align: center; font-size: 1.2rem; font-weight: 700; margin-bottom: 16px; color: #fff; }
.signal-row { border-radius: 7px; padding: 9px 14px; margin-bottom: 6px; font-size: 0.84rem; font-weight: 500; }
.sig-green { background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 3px solid #16a34a; color: #14532d; }
.sig-red   { background: #fff1f2; border: 1px solid #fecaca; border-left: 3px solid #dc2626; color: #7f1d1d; }
.rec-box   { background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #2563eb; border-radius: 10px; padding: 14px 18px; font-size: 0.9rem; color: #1e3a5f; line-height: 1.65; }
</style>
""", unsafe_allow_html=True)

INDUSTRIES     = ['SaaS','FinTech','HealthTech','E-commerce','Logistics','EdTech','CyberSecurity','MarTech','HRTech','LegalTech']
COMPANY_SIZES  = ['1-10','11-50','51-200','201-500','501-1000','1000+']
FUNDING_ROUNDS = {0:"None", 1:"Seed", 2:"Series A", 3:"Series B", 4:"Series C+"}

def get_client():
    try: return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except: st.error("Add GROQ_API_KEY to Streamlit Secrets."); st.stop()

def analyze(data: dict) -> dict:
    client = get_client()
    prompt = f"""You are a B2B sales intelligence AI. Analyze these company buying signals and return ONLY valid JSON, no markdown.

Company Data:
- Name: {data['company_name']}
- Industry: {data['industry']}
- Size: {data['company_size']}
- New Job Postings (30d): {data['new_job_postings_30d']}
- Hiring Sales/Marketing: {data['hiring_sales_marketing']}
- Hiring Engineers: {data['hiring_engineers']}
- Job Posting Growth: {data['job_posting_growth_rate']}
- Days Since Funding: {data['days_since_funding']}
- Funding Amount: ${data['funding_amount_m']}M
- Funding Round: {FUNDING_ROUNDS[data['funding_round']]}
- New Tools Added (90d): {data['new_tools_added_90d']}
- Using Competitor: {data['using_competitor']}
- Tech Stack Size: {data['tech_stack_size']}
- Web Traffic Growth: {data['web_traffic_growth_pct']}%
- LinkedIn Follower Growth: {data['linkedin_follower_growth']}
- News Mentions (30d): {data['news_mentions_30d']}
- Recent Announcement: {data['has_recent_announcement']}
- Visited Pricing Page: {data['visited_pricing_page']}
- Email Engagement Score: {data['email_engagement_score']}
- Days Since Last Touch: {data['days_since_last_touch']}

Return exactly this JSON:
{{
  "intent_score": <float 0.0-1.0>,
  "intent_tier": "Hot" | "Warm" | "Lukewarm" | "Cold",
  "decision": "Buy Now" | "Nurture" | "Monitor" | "Deprioritize",
  "recommended_action": "specific 1-2 sentence action for sales team",
  "top_buying_signals": [
    {{"signal": "signal name", "strength": <float 0.0-1.0>, "reason": "why this matters"}},
    {{"signal": "signal name", "strength": <float 0.0-1.0>, "reason": "why this matters"}},
    {{"signal": "signal name", "strength": <float 0.0-1.0>, "reason": "why this matters"}}
  ],
  "top_missing_signals": [
    {{"signal": "signal name", "gap": "what is missing"}},
    {{"signal": "signal name", "gap": "what is missing"}}
  ],
  "summary": "2-3 sentence summary of buying intent analysis"
}}

Scoring rules:
- Hot: intent_score >= 0.75 (strong signals, act now)
- Warm: intent_score 0.55-0.74 (good signals, follow up soon)
- Lukewarm: intent_score 0.35-0.54 (some signals, nurture)
- Cold: intent_score < 0.35 (weak signals, deprioritize)"""

    raw = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2, max_tokens=1000
    ).choices[0].message.content.strip()

    if "```" in raw:
        raw = raw.split("```")[1].lstrip("json")
    return json.loads(raw.strip().rstrip("`"))


# ── sidebar ──
with st.sidebar:
    st.markdown("## ⚡ IntentPulse")
    st.divider()

    company_name = st.text_input("Company Name", "Acme Corp")
    industry     = st.selectbox("Industry", INDUSTRIES)
    company_size = st.selectbox("Company Size", COMPANY_SIZES)

    st.divider()
    st.markdown("**📋 Hiring Signals**")
    new_postings   = st.slider("New job postings (30d)", 0, 50, 8)
    hiring_sales   = st.checkbox("Hiring Sales / Marketing", True)
    hiring_eng     = st.checkbox("Hiring Engineers", True)
    posting_growth = st.slider("Job posting growth rate", -0.5, 2.0, 0.3, 0.05)

    st.divider()
    st.markdown("**💰 Funding Signals**")
    days_funded  = st.slider("Days since last funding", 0, 730, 60)
    funding_amt  = st.number_input("Funding amount ($M)", 0.0, 500.0, 12.0)
    funding_round = st.selectbox("Funding round", list(FUNDING_ROUNDS.keys()),
                                  format_func=lambda x: FUNDING_ROUNDS[x])

    st.divider()
    st.markdown("**⚙️ Tech Signals**")
    new_tools        = st.slider("New tools added (90d)", 0, 15, 3)
    using_competitor = st.checkbox("Using competitor product", False)
    stack_size       = st.slider("Tech stack size", 5, 80, 25)

    st.divider()
    st.markdown("**📈 Growth Signals**")
    traffic_growth  = st.slider("Web traffic growth (%)", -50, 100, 15)
    linkedin_growth = st.slider("LinkedIn follower growth", -20, 50, 8)
    news_mentions   = st.slider("News mentions (30d)", 0, 20, 3)
    announcement    = st.checkbox("Recent announcement", False)

    st.divider()
    st.markdown("**💌 Engagement**")
    pricing_visit = st.checkbox("Visited pricing page", False)
    email_score   = st.slider("Email engagement score", 0.0, 1.0, 0.35, 0.05)
    days_touch    = st.slider("Days since last touch", 0, 365, 30)

    st.divider()
    score_btn = st.button("🎯 Run IntentPulse", use_container_width=True)


# ── header ──
st.markdown("## 🎯 IntentPulse")
st.divider()

# ── analyze ──
if score_btn:
    payload = {
        "company_name": company_name, "industry": industry,
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

    with st.spinner("Analyzing buying signals…"):
        try:
            r = analyze(payload)
        except json.JSONDecodeError:
            st.error("Couldn't parse AI response. Try again."); st.stop()
        except Exception as e:
            st.error(f"Error: {e}"); st.stop()

    tier   = r.get("intent_tier", "Cold")
    score  = r.get("intent_score", 0)
    colors = {"Hot":"#dc2626","Warm":"#ea580c","Lukewarm":"#d97706","Cold":"#64748b"}
    color  = colors.get(tier, "#64748b")

    # ── tier banner ──
    st.markdown(f'<div class="tier-banner" style="background:{color};">'
                f'{r.get("decision","—")}  ·  {tier}</div>', unsafe_allow_html=True)

    # ── metrics ──
    m1, m2, m3, m4 = st.columns(4, gap="large")
    with m1:
        st.markdown(f'<div class="card"><div class="metric-lbl">Company</div>'
                    f'<div class="metric-val" style="font-size:1.1rem;">{company_name}</div></div>',
                    unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="card"><div class="metric-lbl">Intent Score</div>'
                    f'<div class="metric-val" style="color:{color};">{score*100:.1f}%</div></div>',
                    unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="card"><div class="metric-lbl">Tier</div>'
                    f'<div class="metric-val" style="color:{color};">{tier}</div></div>',
                    unsafe_allow_html=True)
    with m4:
        action_label = "Immediate" if tier == "Hot" else "Scheduled" if tier == "Warm" else "Monitor"
        st.markdown(f'<div class="card"><div class="metric-lbl">Action</div>'
                    f'<div class="metric-val" style="font-size:1.1rem;">{action_label}</div></div>',
                    unsafe_allow_html=True)

    # ── recommendation ──
    st.markdown(f'<div class="rec-box">💡 {r.get("recommended_action","")}</div>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── gauge + signals ──
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("**Intent Score Gauge**")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(score * 100, 1),
            number={"suffix": "%", "font": {"size": 36, "color": "#0f172a"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#94a3b8"},
                "bar":  {"color": color, "thickness": 0.25},
                "bgcolor": "#f8fafc",
                "bordercolor": "#e2e8f0",
                "steps": [
                    {"range": [0,  35],  "color": "#f1f5f9"},
                    {"range": [35, 55],  "color": "#fef9c3"},
                    {"range": [55, 75],  "color": "#ffedd5"},
                    {"range": [75, 100], "color": "#fee2e2"},
                ],
                "threshold": {"line": {"color": "#0f172a", "width": 3}, "value": score * 100}
            }
        ))
        fig.update_layout(
            height=280,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("**Signal Breakdown**")
        buying  = r.get("top_buying_signals", [])
        missing = r.get("top_missing_signals", [])

        if buying:
            st.markdown("🟢 **Active Buying Signals**")
            for s in buying:
                pct = int(s.get("strength", 0) * 100)
                st.markdown(
                    f'<div class="signal-row sig-green">'
                    f'<b>{s["signal"]}</b> — {pct}% strength<br>'
                    f'<span style="font-size:0.78rem;color:#166534;">{s.get("reason","")}</span>'
                    f'</div>', unsafe_allow_html=True)

        if missing:
            st.markdown("🔴 **Weak / Missing Signals**")
            for s in missing:
                st.markdown(
                    f'<div class="signal-row sig-red">'
                    f'<b>{s["signal"]}</b><br>'
                    f'<span style="font-size:0.78rem;color:#991b1b;">{s.get("gap","")}</span>'
                    f'</div>', unsafe_allow_html=True)

    # ── summary ──
    st.divider()
    st.markdown(f'<div class="rec-box">📊 {r.get("summary","")}</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:60px 0;color:#94a3b8;">
        <div style="font-size:3rem;margin-bottom:12px;">🎯</div>
        <div style="font-size:1rem;font-weight:600;color:#475569;">Fill in the signals on the left</div>
        <div style="font-size:0.875rem;margin-top:6px;">Click <b>Detect Buying Intent</b> to run AI analysis</div>
    </div>
    """, unsafe_allow_html=True)
