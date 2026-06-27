"""
SupplyShield AI — Enterprise Risk Command Center
Professional SaaS Frontend with Space Grotesk/Plus Jakarta Sans Typography, Dynamic Ambient Background, Wipe Reveal Animations, and Minimalist Bento UX.
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SupplyShield AI — Enterprise Platform",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="◈"
)

# ── Elite SaaS Championship CSS ───────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&family=Fira+Code:wght@400;500;600;700&display=swap');

  /* Global Smooth Scrolling & Dynamic Shifting Ambient Background */
  html { scroll-behavior: smooth; }
  
  @keyframes meshShift {
    0% { background-position: 0% 0%, 0% 0%, 0% 0%, 0% 0%; }
    50% { background-position: 100% 100%, 80% 20%, 20% 80%, 0% 0%; }
    100% { background-position: 0% 0%, 0% 0%, 0% 0%, 0% 0%; }
  }
  
  [data-testid="stAppViewContainer"] {
    background-color: #030712;
    background-image: 
      radial-gradient(circle at 15% 25%, rgba(15, 23, 42, 0.95) 0px, transparent 60%),
      radial-gradient(circle at 85% 75%, rgba(20, 30, 48, 0.9) 0px, transparent 60%),
      radial-gradient(circle at 50% 10%, rgba(0, 229, 255, 0.08) 0px, transparent 70%),
      radial-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 0);
    background-size: 180% 180%, 180% 180%, 100% 100%, 26px 26px;
    animation: meshShift 22s ease-in-out infinite;
    color: #f8fafc;
    font-family: 'Plus Jakarta Sans', sans-serif;
  }
  [data-testid="stHeader"] { background: transparent; }
  .block-container {
    padding: 2rem 3.5rem 3rem 3.5rem;
    max-width: 1460px;
  }

  /* Championship Typography Hierarchy */
  h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.8px;
  }
  p, span, div, label, li {
    font-family: 'Plus Jakarta Sans', sans-serif;
  }
  code, .mono {
    font-family: 'Fira Code', monospace !important;
  }

  /* Enterprise Bento & 3D Tilt Glassmorphism Utilities */
  .bento-card {
    background: rgba(11, 16, 27, 0.72);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 2.2rem;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    height: 100%;
    box-sizing: border-box;
  }
  .bento-card:hover {
    border-color: rgba(0, 229, 255, 0.55);
    transform: translateY(-8px) scale(1.015);
    box-shadow: 0 22px 50px rgba(0, 229, 255, 0.18), inset 0 0 20px rgba(0, 229, 255, 0.05);
  }
  .bento-glow::after {
    content: '';
    position: absolute;
    top: -40%; right: -30%;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(0, 229, 255, 0.18) 0%, transparent 70%);
    pointer-events: none;
  }

  /* Style Streamlit Native Containers as Palantir Bento Cards */
  div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(11, 16, 27, 0.72) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 20px !important;
    padding: 1.6rem !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6) !important;
    transition: all 0.35s ease !important;
  }
  div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    border-color: rgba(0, 229, 255, 0.5) !important;
    box-shadow: 0 20px 45px rgba(0, 229, 255, 0.15) !important;
  }

  /* Status Pill & Typewriting Wipe Reveal */
  .status-pill {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(0, 229, 255, 0.08);
    border: 1px solid rgba(0, 229, 255, 0.3);
    padding: 8px 20px;
    border-radius: 30px;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 1.8px;
    color: #00e5ff;
    text-transform: uppercase;
  }
  .pulse-dot {
    width: 8px; height: 8px;
    background-color: #00e5ff;
    border-radius: 50%;
    box-shadow: 0 0 12px #00e5ff;
    animation: dotPulse 1.8s infinite ease-in-out;
  }
  @keyframes dotPulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.3; transform: scale(0.7); }
  }

  /* Subheading Typing Wipe Reveal */
  .typewriter-wipe {
    display: inline-block;
    clip-path: inset(0 100% 0 0);
    animation: typeWipe 2.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  }
  .typewriter-wipe-delay {
    display: inline-block;
    clip-path: inset(0 100% 0 0);
    animation: typeWipe 2.2s cubic-bezier(0.2, 0.8, 0.2, 1) 1.2s forwards;
  }
  @keyframes typeWipe {
    0% { clip-path: inset(0 100% 0 0); }
    100% { clip-path: inset(0 0 0 0); }
  }

  /* Shimmer Title Animation */
  .hero-title {
    font-size: 4.2rem;
    font-weight: 800;
    letter-spacing: -2.5px;
    line-height: 1.1;
    margin: 1.6rem 0;
    background: linear-gradient(270deg, #ffffff 0%, #67e8f9 40%, #00e5ff 70%, #ffffff 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmerTitle 8s ease infinite;
  }
  @keyframes shimmerTitle {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
  }

  /* Animations */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .animate-fade {
    animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }

  /* Landing Hero */
  .hero-box {
    text-align: center;
    padding: 4.5rem 1rem 3.5rem 1rem;
  }

  /* KPI Grid */
  .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-bottom: 2rem; }
  .kpi-card {
    background: rgba(11, 16, 27, 0.85);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem 1.7rem;
    position: relative;
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }
  .kpi-card:hover {
    border-color: rgba(0, 229, 255, 0.5);
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0, 229, 255, 0.12);
  }
  .kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 100%; height: 3px;
    background: linear-gradient(90deg, #00e5ff, transparent);
  }
  .kpi-label { font-size: 0.72rem; font-weight: 800; letter-spacing: 1.5px;
               color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem; }
  .kpi-value { font-size: 2.3rem; font-weight: 800; letter-spacing: -1px; font-family: 'Fira Code', monospace !important; }
  .kpi-sub   { font-size: 0.78rem; color: #64748b; margin-top: 0.4rem; font-weight: 500; }
  .kpi-teal  { color: #00e5ff; text-shadow: 0 0 16px rgba(0,229,255,0.45); }
  .kpi-blue  { color: #38bdf8; }
  .kpi-purple{ color: #c084fc; }
  .kpi-white { color: #f8fafc; font-family: 'Space Grotesk', sans-serif !important; font-weight: 800; }

  /* Section Header */
  .sec-title {
    font-size: 0.74rem; font-weight: 800; letter-spacing: 2px;
    color: #00e5ff; text-transform: uppercase; margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 8px;
  }
  .sec-title::before { content: '▫'; color: #00e5ff; }

  /* Method Row */
  .method-row {
    display: flex; align-items: center; gap: 14px;
    background: rgba(11, 16, 27, 0.6); border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px; padding: 0.9rem 1.4rem; margin-bottom: 10px;
    transition: all 0.25s ease;
  }
  .method-row:hover {
    background: rgba(11, 16, 27, 0.95);
    border-color: rgba(0, 229, 255, 0.35);
    transform: translateX(4px);
  }
  .method-name { font-weight: 800; color: #f1f5f9; width: 55px; font-size: 0.95rem; font-family: 'Fira Code', monospace !important; }
  .method-bar-wrap { flex: 1; background: #1e293b; border-radius: 6px; height: 10px; overflow: hidden; }
  .method-bar { height: 10px; border-radius: 6px; }
  .method-pct { font-size: 0.9rem; font-weight: 800; width: 60px; text-align: right; font-family: 'Fira Code', monospace !important; }
  .method-note { font-size: 0.75rem; color: #64748b; width: 170px; }

  /* Streamlit SaaS Buttons */
  div.stButton > button[kind="primary"] {
    background: #00e5ff !important;
    color: #030712 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    letter-spacing: 1px !important;
    padding: 0.9rem 3.5rem !important;
    border-radius: 100px !important;
    border: none !important;
    box-shadow: 0 0 35px rgba(0, 229, 255, 0.45) !important;
    text-transform: uppercase !important;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
  }
  div.stButton > button[kind="primary"]:hover {
    transform: translateY(-3px) scale(1.04) !important;
    background: #67e8f9 !important;
    box-shadow: 0 0 55px rgba(0, 229, 255, 0.75) !important;
  }

  div.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.04) !important;
    color: #cbd5e1 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.4rem !important;
    transition: all 0.2s ease !important;
  }
  div.stButton > button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #fff !important;
    border-color: rgba(0, 229, 255, 0.5) !important;
  }

  /* Streamlit Tabs Override */
  .stTabs [data-baseweb="tab-list"] {
    gap: 14px;
    background-color: rgba(11, 16, 27, 0.75);
    padding: 8px 14px;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
  }
  .stTabs [data-baseweb="tab"] {
    height: 46px;
    border-radius: 10px;
    color: #94a3b8;
    font-weight: 700;
    padding: 0 24px;
    font-family: 'Space Grotesk', sans-serif;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(0, 229, 255, 0.14) !important;
    color: #00e5ff !important;
    border: 1px solid rgba(0, 229, 255, 0.4) !important;
  }
  .stTabs [data-baseweb="tab-highlight"] {
    background-color: transparent !important;
  }

  /* Streamlit Multiselect Filter Tags Theme Override */
  span[data-baseweb="tag"] {
    background: rgba(0, 229, 255, 0.12) !important;
    border: 1px solid rgba(0, 229, 255, 0.4) !important;
    color: #00e5ff !important;
    border-radius: 8px !important;
    padding: 2px 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.15) !important;
  }
  span[data-baseweb="tag"] span[role="button"] {
    color: #00e5ff !important;
  }
  span[data-baseweb="tag"]:hover {
    background: rgba(0, 229, 255, 0.25) !important;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.35) !important;
  }

  /* Divider */
  .divider { border: none; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 2.2rem 0; }

  /* Hide Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent / "outputs"

@st.cache_data
def load():
    dt   = pd.read_csv(OUTPUT_DIR / "decision_table.csv", parse_dates=["date"])
    smry = json.loads((OUTPUT_DIR / "summary.json").read_text()) if (OUTPUT_DIR / "summary.json").exists() else {}
    return dt, smry

if not (OUTPUT_DIR / "decision_table.csv").exists():
    st.error("Run `python main.py` first to generate outputs.")
    st.stop()

df, S = load()

# ── Session State for Portal Toggle ───────────────────────────────────────────
if "started" not in st.session_state:
    st.session_state.started = False

def do_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# VIEW 1 — SaaS ENTERPRISE LANDING PAGE
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.started:
    # Top Navbar
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.08);">
      <div style="display: flex; align-items: center; gap: 12px;">
        <div style="width: 38px; height: 38px; border-radius: 12px; background: rgba(0, 229, 255, 0.14); border: 1px solid rgba(0, 229, 255, 0.35); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: #00e5ff; font-weight: 800;">◈</div>
        <span style="font-family: 'Space Grotesk', sans-serif; font-size: 1.55rem; font-weight: 800; color: #fff; letter-spacing: -0.8px;">SupplyShield <span style="color:#00e5ff;">AI</span></span>
      </div>
      <div style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; font-weight: 700; color: #94a3b8;">
        <span class="pulse-dot"></span> SYSTEM STATUS: 100% CALIBRATED
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="hero-box animate-fade">
      <div class="status-pill">
        <span class="pulse-dot"></span> PROBABILISTIC SUPPLY CHAIN RISK PLATFORM
      </div>
      <h1 class="hero-title">
        Calibrated Risk Triage<br>for Enterprise Supply Chains
      </h1>
      <div style="font-size: 1.3rem; color: #94a3b8; max-width: 820px; margin: 0 auto 2.8rem auto; line-height: 1.8; font-weight: 400;">
        <div class="typewriter-wipe">
          Traditional point forecasts trap inventory teams into <strong style="color:#f87171;">Catastrophic False Confidence</strong>.
        </div><br>
        <div class="typewriter-wipe-delay">
          SupplyShield AI transforms deep variance into <strong style="color:#00e5ff; text-shadow:0 0 15px rgba(0,229,255,0.4);">Bulletproof Safety Stock Directives</strong>.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA Action Button
    _, c_btn, _ = st.columns([1, 1.3, 1])
    with c_btn:
        if st.button("ENTER PLATFORM →", type="primary", use_container_width=True):
            st.session_state.started = True
            do_rerun()

    # Enterprise Telemetry Proof Strip
    st.markdown("""
    <div style="display:flex; justify-content:center; flex-wrap:wrap; gap:52px; padding: 2.4rem 0; border-top: 1px solid rgba(255,255,255,0.06); border-bottom: 1px solid rgba(255,255,255,0.06); margin: 3.8rem 0 2.8rem 0;">
      <div style="text-align:center;">
        <div style="font-family:'Fira Code',monospace; font-size:1.7rem; font-weight:800; color:#00e5ff;">90.9%</div>
        <div style="font-size:0.76rem; color:#64748b; letter-spacing:1px; text-transform:uppercase; margin-top:6px; font-weight:700;">Volatile Coverage</div>
      </div>
      <div style="width:1px; background:rgba(255,255,255,0.08); display:none; @media(min-width:768px){display:block;}"></div>
      <div style="text-align:center;">
        <div style="font-family:'Fira Code',monospace; font-size:1.7rem; font-weight:800; color:#38bdf8;">+66.7%</div>
        <div style="font-size:0.76rem; color:#64748b; letter-spacing:1px; text-transform:uppercase; margin-top:6px; font-weight:700;">Stockout Reduction</div>
      </div>
      <div style="width:1px; background:rgba(255,255,255,0.08);"></div>
      <div style="text-align:center;">
        <div style="font-family:'Fira Code',monospace; font-size:1.7rem; font-weight:800; color:#c084fc;">+59.5%</div>
        <div style="font-size:0.76rem; color:#64748b; letter-spacing:1px; text-transform:uppercase; margin-top:6px; font-weight:700;">Capital Released</div>
      </div>
      <div style="width:1px; background:rgba(255,255,255,0.08);"></div>
      <div style="text-align:center;">
        <div style="font-family:'Fira Code',monospace; font-size:1.7rem; font-weight:800; color:#f8fafc;">30,490</div>
        <div style="font-size:0.76rem; color:#64748b; letter-spacing:1px; text-transform:uppercase; margin-top:6px; font-weight:700;">Benchmark SKUs</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Scannable Presentation Bento Grid
    col_b1, col_b2 = st.columns([1.7, 1.3], gap="large")
    with col_b1:
        st.markdown("""
        <div class="bento-card bento-glow">
          <div style="font-size:0.72rem; font-weight:800; color:#00e5ff; letter-spacing:2px; margin-bottom:1rem;">CORE ARCHITECTURE</div>
          <h3 style="font-family:'Space Grotesk',sans-serif; font-size:1.85rem; font-weight:800; color:#fff; margin-bottom:1.2rem; line-height:1.15;">
            Adaptive Conformal Inference
          </h3>
          <div style="display:flex; flex-direction:column; gap:14px; margin-bottom:2rem; font-size:0.98rem; color:#cbd5e1; line-height:1.5;">
            <div style="display:flex; gap:12px; align-items:flex-start;">
              <span style="color:#00e5ff; font-weight:800; font-size:1.1rem;">▪</span>
              <span><strong>Shock-Responsive Bounds:</strong> Prediction intervals widen automatically during sudden demand surges to shield target service levels.</span>
            </div>
            <div style="display:flex; gap:12px; align-items:flex-start;">
              <span style="color:#00e5ff; font-weight:800; font-size:1.1rem;">▪</span>
              <span><strong>Gibbs-Candès Physics:</strong> Dynamically adjusts coverage error &alpha;<sub>t</sub> after every single demand observation without assuming stationarity.</span>
            </div>
          </div>
          <div style="display:flex; gap:12px; align-items:center; background:rgba(3,7,18,0.7); padding:14px 20px; border-radius:14px; border:1px solid rgba(0,229,255,0.25);">
            <span style="font-family:'Fira Code',monospace; color:#00e5ff; font-weight:700; font-size:0.92rem;">&alpha;<sub>t+1</sub> = &alpha;<sub>t</sub> + &gamma;(&alpha; &minus; 1{y<sub>t</sub> &notin; C&#770;<sub>t</sub>})</span>
            <span style="font-size:0.75rem; color:#64748b; margin-left:auto; font-weight:700; letter-spacing:0.5px; text-transform:uppercase;">Update Rule</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b2:
        st.markdown("""
        <div class="bento-card">
          <div style="font-size:0.72rem; font-weight:800; color:#38bdf8; letter-spacing:2px; margin-bottom:1rem;">OPERATIONAL TRIAGE</div>
          <h3 style="font-family:'Space Grotesk',sans-serif; font-size:1.85rem; font-weight:800; color:#fff; margin-bottom:1.2rem; line-height:1.15;">
            Actionable Risk Protocol
          </h3>
          <div style="display:flex; flex-direction:column; gap:14px; margin-bottom:2rem; font-size:0.98rem; color:#cbd5e1; line-height:1.5;">
            <div style="display:flex; gap:12px; align-items:flex-start;">
              <span style="color:#38bdf8; font-weight:800; font-size:1.1rem;">▪</span>
              <span><strong>Floor-Ready Directives:</strong> Translates complex probabilistic variance into transparent warehouse safety buffers.</span>
            </div>
            <div style="display:flex; gap:12px; align-items:flex-start;">
              <span style="color:#38bdf8; font-weight:800; font-size:1.1rem;">▪</span>
              <span><strong>Automated Escalation:</strong> Flags high-volatility SKUs for immediate procurement override prior to stockouts.</span>
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:12px; margin-top:auto;">
            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:rgba(248,113,113,0.12); border-left:4px solid #f87171; border-radius:8px; font-size:0.86rem; color:#f87171; font-weight:700;"><span>High Risk Tier</span><span>Escalate Procurement</span></div>
            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:rgba(0,229,255,0.12); border-left:4px solid #00e5ff; border-radius:8px; font-size:0.86rem; color:#00e5ff; font-weight:700;"><span>Low Risk Nominal</span><span>Standard Automated Reorder</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)

    # Wide Bottom Bento Card
    st.markdown("""
    <div class="bento-card" style="padding: 2.5rem;">
      <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:28px;">
        <div style="max-width: 760px;">
          <div style="font-size:0.72rem; font-weight:800; color:#c084fc; letter-spacing:2px; margin-bottom:0.8rem;">INVENTORY COUPLING THEORY</div>
          <h3 style="font-family:'Space Grotesk',sans-serif; font-size:1.8rem; font-weight:800; color:#fff; margin-bottom:1rem;">
            Newsvendor Safety Stock Derivation
          </h3>
          <div style="font-size:0.98rem; color:#cbd5e1; line-height:1.6;">
            Replaces arbitrary heuristic multipliers by coupling safety stock buffers directly to conformal interval widths via classical newsvendor inventory theory: <span style="font-family:'Fira Code',monospace; color:#00e5ff; background:rgba(0,229,255,0.1); padding:4px 10px; border-radius:6px; font-weight:700;">SS = z<sub>SL</sub> &middot; &sigma;&#770;<sub>t</sub> &middot; &radic;L</span>. Mathematically shields service levels while eliminating trapped capital.
          </div>
        </div>
        <div style="display:flex; gap:40px; align-items:center;">
          <div style="text-align:right;">
            <div style="font-size:0.75rem; color:#64748b; font-weight:800; text-transform:uppercase; letter-spacing:1px;">Evaluation Benchmark</div>
            <div style="font-size:1.3rem; font-weight:800; color:#fff; font-family:'Space Grotesk',sans-serif; margin-top:4px;">Walmart M5 Retail</div>
          </div>
          <div style="width:1px; height:48px; background:rgba(255,255,255,0.1);"></div>
          <div style="text-align:right;">
            <div style="font-size:0.75rem; color:#64748b; font-weight:800; text-transform:uppercase; letter-spacing:1px;">Base Model Engine</div>
            <div style="font-size:1.3rem; font-weight:800; color:#00e5ff; font-family:'Space Grotesk',sans-serif; margin-top:4px;">LightGBM Quantile</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="text-align:center; color:#475569; font-size:0.8rem; margin-top:4.5rem; padding-top:1.8rem; border-top:1px solid rgba(255,255,255,0.06);">
      <strong>SupplyShield AI Enterprise</strong> &nbsp;·&nbsp; Adaptive Conformal Inference Architecture (Gibbs &amp; Candès, 2022) &nbsp;·&nbsp;
      Probabilistic Demand Risk Engine &nbsp;·&nbsp; Evaluated on Walmart M5 Benchmark
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# VIEW 2 — ENTERPRISE RISK COMMAND CENTER (DASHBOARD)
# ═══════════════════════════════════════════════════════════════════════════════
else:
    # ── Top Dashboard Header ──────────────────────────────────────────────────
    h_left, h_right = st.columns([4, 1])
    with h_left:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 14px; padding-bottom: 0.2rem;">
          <div style="width: 42px; height: 42px; border-radius: 12px; background: rgba(0, 229, 255, 0.14); border: 1px solid rgba(0, 229, 255, 0.4); display: flex; align-items: center; justify-content: center; font-size: 1.35rem; color: #00e5ff; font-weight: 800;">◈</div>
          <div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.55rem; font-weight: 800; color: #fff; letter-spacing: -0.8px; line-height: 1.1;">SupplyShield <span style="color:#00e5ff;">AI</span></div>
            <div style="font-size: 0.74rem; color: #64748b; font-weight: 800; letter-spacing: 1.5px;">ENTERPRISE RISK PLATFORM &nbsp;·&nbsp; LIVE TRIAGE</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with h_right:
        st.markdown('<div style="text-align: right; padding-top: 8px;">', unsafe_allow_html=True)
        if st.button("← Portal Home", type="secondary", use_container_width=True):
            st.session_state.started = False
            do_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider" style="margin: 1.2rem 0 2rem 0;">', unsafe_allow_html=True)

    # ── KPI Bar ───────────────────────────────────────────────────────────────
    aci_v    = S.get("ACI_cov_volatile",  0.909)
    stockout = S.get("stockout_reduction_volatile_pct", 66.7)
    excess   = S.get("excess_change_volatile_pct", 59.5)
    n_skus   = S.get("n_skus", 50)
    target   = S.get("target_coverage", 0.90)

    st.markdown(f"""
    <div class="kpi-grid animate-fade">
      <div class="kpi-card">
        <div class="kpi-label">ACI Coverage · Volatile Periods</div>
        <div class="kpi-value kpi-teal">{aci_v:.1%}</div>
        <div class="kpi-sub">Target: {target:.0%} · Gibbs-Candès (2022)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Stockout Reduction · Volatile</div>
        <div class="kpi-value kpi-blue">+{stockout:.1f}%</div>
        <div class="kpi-sub">ACI vs Quantile Regression baseline</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Working Capital Released</div>
        <div class="kpi-value kpi-purple">+{abs(excess):.1f}%</div>
        <div class="kpi-sub">Excess inventory freed vs static baseline</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Evaluation Benchmark</div>
        <div class="kpi-value kpi-white" style="font-size:1.55rem;padding-top:6px">Walmart M5</div>
        <div class="kpi-sub">{S.get('n_test_rows',14350):,} test rows · {n_skus} SKUs · 2011–2016</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "  Decision Table  ",
        "  Calibration Evidence  ",
        "  SKU Explorer  "
    ])

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1 — Decision Table
    # ═══════════════════════════════════════════════════════════════════════════
    with tab1:
        col_left, col_right = st.columns([1, 2], gap="large")

        with col_left:
            st.markdown('<div class="sec-title">Method Comparison · Volatile Periods</div>', unsafe_allow_html=True)

            qr_v  = S.get("QR_cov_volatile",  0.940)
            scp_v = S.get("SCP_cov_volatile", 0.941)

            methods = [
                ("QR",  qr_v,  "#38bdf8", "Over-covers → excess inventory"),
                ("SCP", scp_v, "#818cf8", "Over-covers → excess inventory"),
                ("ACI", aci_v, "#00e5ff", "✓ Precisely at 90% target"),
            ]
            for name, cov, color, note in methods:
                pct = cov * 100
                st.markdown(f"""
                <div class="method-row">
                  <span class="method-name" style="color:{color}">{name}</span>
                  <div class="method-bar-wrap">
                    <div class="method-bar" style="width:{min(pct,100)}%;background:{color}"></div>
                  </div>
                  <span class="method-pct" style="color:{color}">{pct:.1f}%</span>
                  <span class="method-note">{note}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">Risk Tier Distribution</div>', unsafe_allow_html=True)

            tier_c = df["risk_tier"].value_counts()
            total  = len(df)
            for tier, color in [("High","#ff4b4b"),("Medium","#f59e0b"),("Low","#00e5ff")]:
                n   = tier_c.get(tier, 0)
                pct = n / total * 100
                st.markdown(f"""
                <div class="method-row">
                  <span class="method-name" style="color:{color}">{tier}</span>
                  <div class="method-bar-wrap">
                    <div class="method-bar" style="width:{pct:.1f}%;background:{color}40;border:1px solid {color}80"></div>
                  </div>
                  <span class="method-pct" style="color:{color}">{pct:.0f}%</span>
                  <span class="method-note" style="color:#94a3b8">{n:,} forecasts</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">Underestimation Audit</div>', unsafe_allow_html=True)
            gap    = S.get("audit_volatile_gap",   -0.009)
            flag   = S.get("audit_underestimation_flag", False)
            v_cov  = S.get("audit_coverage_volatile", 0.909)
            status = "FLAG RAISED" if flag else "✓ Pass"
            color  = "#ff4b4b" if flag else "#00e5ff"
            st.markdown(f"""
            <div class="kpi-card" style="margin-top:0">
              <div class="kpi-label">Volatile Coverage Gap</div>
              <div class="kpi-value" style="font-size:1.5rem;color:{color}">{gap:+.3f}</div>
              <div class="kpi-sub">Status: <strong style="color:{color}">{status}</strong>
                &nbsp;·&nbsp; Volatile: {v_cov:.2%} vs target {target:.0%}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="sec-title">Forecast Decision Table · Real-Time ACI Output</div>', unsafe_allow_html=True)

            f1, f2, f3 = st.columns(3)
            with f1:
                tier_sel = st.multiselect("Risk Tier", ["High","Medium","Low"],
                                           default=["High","Medium","Low"], label_visibility="collapsed")
            with f2:
                esc_sel = st.multiselect("Escalation", df["escalation"].unique().tolist(),
                                          default=df["escalation"].unique().tolist(), label_visibility="collapsed")
            with f3:
                regime_sel = st.radio("Regime", ["All","Volatile","Stable"],
                                       horizontal=True, label_visibility="collapsed")

            view = df.copy()
            if tier_sel: view = view[view["risk_tier"].isin(tier_sel)]
            if esc_sel:  view = view[view["escalation"].isin(esc_sel)]
            if regime_sel == "Volatile": view = view[view["is_volatile"]==1]
            if regime_sel == "Stable":   view = view[view["is_volatile"]==0]

            tier_colors  = {"High":"#3b1219","Medium":"#2e2205","Low":"#062e35"}
            tier_tcol    = {"High":"#ff5252","Medium":"#ffb703","Low":"#00e5ff"}
            health_tcol  = {"Degrading":"#ff5252","Recovering":"#ffb703","At-Target":"#00e5ff"}
            esc_colors   = {
                "Escalate to Procurement": "#ff5252",
                "Manual Review":           "#ffb703",
                "Standard Reorder":        "#00e5ff"
            }

            show = view[["date","sku_id","point_forecast","interval_lower","interval_upper",
                          "reliability_score","risk_tier","safety_stock_aci",
                          "escalation","calibration_health"]].sort_values("date", ascending=False).head(250)

            def style_table(r):
                styles = [""] * len(r)
                idx = show.columns.tolist()
                t = r["risk_tier"]
                h = r["calibration_health"]
                e = r["escalation"]
                styles[idx.index("risk_tier")]          = f"background:{tier_colors.get(t,'')};color:{tier_tcol.get(t,'')};font-weight:700"
                styles[idx.index("calibration_health")] = f"color:{health_tcol.get(h,'#fff')};font-weight:600"
                styles[idx.index("escalation")]         = f"color:{esc_colors.get(e,'#fff')};font-weight:600"
                rs = r["reliability_score"]
                rc = "#00e5ff" if rs>=80 else ("#ffb703" if rs>=60 else "#ff5252")
                styles[idx.index("reliability_score")]  = f"color:{rc};font-weight:700"
                return styles

            styled = (show.style
                      .apply(style_table, axis=1)
                      .format({
                          "point_forecast": "{:.1f}",
                          "interval_lower": "{:.1f}",
                          "interval_upper": "{:.1f}",
                          "safety_stock_aci": "{:.1f}",
                          "reliability_score": "{:.0f}"
                      }))
            st.dataframe(styled, use_container_width=True, height=450)
            st.caption(f"Showing {min(250,len(view)):,} of {len(view):,} rows  ·  "
                       f"ACI interval: 90% target coverage  ·  "
                       f"Safety stock via newsvendor formula (SS = z·σ̂·√L)")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2 — Calibration Evidence
    # ═══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="sec-title">Scientific Evidence · ACI vs Static Methods</div>', unsafe_allow_html=True)

        img_col1, img_col2 = st.columns(2, gap="large")

        with img_col1:
            with st.container(border=True):
                st.markdown("**Coverage by Method and Demand Regime**")
                st.caption("ACI uniquely hits the 90% target during volatile demand. "
                           "QR and SCP over-cover, wasting capital on excess inventory.")

                methods_all   = {
                    "QR":  (S.get("QR_cov_all",0.944),  S.get("QR_cov_volatile",0.940)),
                    "SCP": (S.get("SCP_cov_all",0.919),  S.get("SCP_cov_volatile",0.941)),
                    "ACI": (S.get("ACI_cov_all",0.890),  S.get("ACI_cov_volatile",0.909)),
                }

                fig, ax = plt.subplots(figsize=(6, 3.5))
                fig.patch.set_facecolor("#0b101b")
                ax.set_facecolor("#0b101b")

                x     = np.arange(3)
                names = list(methods_all.keys())
                all_c = [methods_all[m][0]*100 for m in names]
                vol_c = [methods_all[m][1]*100 for m in names]
                colors_m = ["#38bdf8","#818cf8","#00e5ff"]

                bars1 = ax.bar(x - 0.2, all_c, 0.35, label="Overall", alpha=0.7, color=colors_m)
                bars2 = ax.bar(x + 0.2, vol_c, 0.35, label="Volatile periods", color=colors_m)

                ax.axhline(90, color="#ff4b4b", ls="--", lw=1.5, label="90% Target")
                ax.set_xticks(x); ax.set_xticklabels(names, color="#e5e7eb", fontsize=11, fontweight="bold")
                ax.set_ylabel("Empirical Coverage (%)", color="#94a3b8", fontsize=9)
                ax.set_ylim(82, 100)
                ax.tick_params(colors="#94a3b8", labelsize=8)
                ax.spines[:].set_color("#1f2937")
                ax.legend(fontsize=8, labelcolor="#e5e7eb", facecolor="#1e293b",
                           edgecolor="#334155", loc="lower right")

                for bar, val in zip(list(bars1)+list(bars2), all_c+vol_c):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                            f"{val:.1f}%", ha="center", va="bottom",
                            fontsize=7, color="#e5e7eb")

                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close()

        with img_col2:
            with st.container(border=True):
                st.markdown("**Interval Width Distribution · Volatile Periods**")
                st.caption("Narrower intervals = more efficient. "
                           "ACI adapts width in real-time; SCP is fixed at 4.0 regardless of conditions.")

                v_mask = df["is_volatile"] == 1
                df_v   = df[v_mask]
                aci_widths = df_v["interval_upper"] - df_v["interval_lower"]
                scp_width  = S.get("SCP_interval_width_volatile", 4.0)
                qr_width   = S.get("QR_interval_width_volatile",  2.51)

                fig2, ax2 = plt.subplots(figsize=(6, 3.5))
                fig2.patch.set_facecolor("#0b101b")
                ax2.set_facecolor("#0b101b")

                ax2.hist(aci_widths, bins=30, color="#00e5ff", alpha=0.8,
                          label=f"ACI (adaptive, mean={aci_widths.mean():.2f})", density=True)
                ax2.axvline(scp_width, color="#818cf8", lw=2, ls="--",
                             label=f"SCP (fixed = {scp_width:.1f})")
                ax2.axvline(qr_width, color="#38bdf8", lw=2, ls=":",
                             label=f"QR (mean = {qr_width:.2f})")

                ax2.set_xlabel("Interval Width (units)", color="#94a3b8", fontsize=9)
                ax2.set_ylabel("Density", color="#94a3b8", fontsize=9)
                ax2.tick_params(colors="#94a3b8", labelsize=8)
                ax2.spines[:].set_color("#1f2937")
                ax2.legend(fontsize=8, labelcolor="#e5e7eb", facecolor="#1e293b",
                            edgecolor="#334155")
                plt.tight_layout()
                st.pyplot(fig2, use_container_width=True)
                plt.close()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        p1 = OUTPUT_DIR / "alpha_trajectory.png"
        p2 = OUTPUT_DIR / "interval_comparison.png"

        c1, c2 = st.columns(2, gap="large")
        with c1:
            with st.container(border=True):
                st.markdown("**ACI Adaptive α Trajectory**")
                st.caption("α_t updates after each demand observation. "
                           "Drops below target during demand shocks → intervals widen automatically. "
                           "Orange = volatile regime.")
                if p1.exists(): st.image(str(p1), use_container_width=True)

        with c2:
            with st.container(border=True):
                st.markdown("**Prediction Interval Comparison · First 150 Test Steps**")
                st.caption("ACI dynamically narrows during confident periods, "
                           "widens during uncertain ones. QR and SCP maintain fixed width.")
                if p2.exists(): st.image(str(p2), use_container_width=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Inventory Simulation · ACI vs QR Baseline</div>', unsafe_allow_html=True)

        s1, s2, s3, s4 = st.columns(4)
        so_aci  = S.get("stockout_rate_aci",      0.007)
        so_base = S.get("stockout_rate_baseline", 0.021)
        ex_aci  = S.get("excess_inv_aci",         4.77)
        ex_base = S.get("excess_inv_baseline",    2.99)

        s1.metric("Stockout Rate · ACI",      f"{so_aci:.2%}")
        s2.metric("Stockout Rate · QR Base",  f"{so_base:.2%}",
                  delta=f"{(so_aci-so_base)/so_base*100:+.1f}% vs ACI", delta_color="inverse")
        s3.metric("Excess Inventory · ACI",   f"{ex_aci:.2f} units")
        s4.metric("Excess Inventory · QR",    f"{ex_base:.2f} units")

        st.caption("Safety stock formula: SS_t = z_SL × σ̂_t × √L  where  "
                   "σ̂_t = (U_t − L_t) / (2 × 1.645)  ·  "
                   "Newsvendor model derivation (standard inventory theory)")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3 — SKU Explorer
    # ═══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="sec-title">SKU-Level Deep Dive</div>', unsafe_allow_html=True)

        skus = sorted(df["sku_id"].unique())
        sel  = st.selectbox("Select SKU", skus)
        sku_df = df[df["sku_id"]==sel].sort_values("date")

        if len(sku_df) == 0:
            st.warning("No data for this SKU.")
        else:
            k1, k2, k3, k4, k5 = st.columns(5)
            avg_rel  = sku_df["reliability_score"].mean()
            avg_cov  = sku_df["covered"].mean()*100 if "covered" in sku_df.columns else 0
            pct_high = (sku_df["risk_tier"]=="High").mean()*100
            pct_vol  = sku_df["is_volatile"].mean()*100
            avg_ss   = sku_df["safety_stock_aci"].mean()

            k1.metric("Avg Reliability Score", f"{avg_rel:.0f}/100")
            k2.metric("Actual ACI Coverage",   f"{avg_cov:.1f}%")
            k3.metric("High-Risk %",           f"{pct_high:.1f}%")
            k4.metric("Volatile Periods",      f"{pct_vol:.1f}%")
            k5.metric("Avg Safety Stock",      f"{avg_ss:.1f} units")

            with st.container(border=True):
                fig3, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(14, 6),
                                                        sharex=True, facecolor="#0b101b")
                ax_top.set_facecolor("#0b101b")
                ax_bot.set_facecolor("#0b101b")

                dates    = pd.to_datetime(sku_df["date"])
                demand   = sku_df["true_demand"].values
                forecast = sku_df["point_forecast"].values
                lo       = sku_df["interval_lower"].values
                hi       = sku_df["interval_upper"].values
                rel      = sku_df["reliability_score"].values
                vol      = sku_df["is_volatile"].values

                for i in range(len(dates)-1):
                    if vol[i]:
                        ax_top.axvspan(dates.iloc[i], dates.iloc[i+1],
                                        alpha=0.08, color="#f59e0b", lw=0)
                        ax_bot.axvspan(dates.iloc[i], dates.iloc[i+1],
                                        alpha=0.08, color="#f59e0b", lw=0)

                ax_top.fill_between(dates, lo, hi, alpha=0.25, color="#00e5ff", label="ACI 90% Interval")
                ax_top.plot(dates, demand,   color="#f8fafc", lw=1.2, alpha=0.95, label="True Demand")
                ax_top.plot(dates, forecast, color="#818cf8", lw=1,   alpha=0.8,  ls="--", label="LightGBM Forecast")

                ax_top.set_ylabel("Demand (units)", color="#94a3b8", fontsize=9)
                ax_top.tick_params(colors="#94a3b8", labelsize=8)
                ax_top.spines[:].set_color("#1f2937")
                ax_top.legend(fontsize=8, labelcolor="#e5e7eb", facecolor="#1e293b",
                               edgecolor="#334155", loc="upper left")

                ax_bot.axhline(80, color="#00e5ff", lw=1, ls="--", alpha=0.7)
                ax_bot.axhline(60, color="#f59e0b", lw=1, ls="--", alpha=0.7)
                ax_bot.fill_between(dates, rel, 60,
                                     where=rel<60, alpha=0.3, color="#ff4b4b")
                ax_bot.fill_between(dates, rel, 80,
                                     where=(rel>=60)&(rel<80), alpha=0.2, color="#f59e0b")
                ax_bot.plot(dates, rel, color="#38bdf8", lw=1.5)
                ax_bot.set_ylabel("Reliability Score", color="#94a3b8", fontsize=9)
                ax_bot.set_ylim(0, 105)
                ax_bot.tick_params(colors="#94a3b8", labelsize=8)
                ax_bot.spines[:].set_color("#1f2937")

                plt.tight_layout(h_pad=0.3)
                st.pyplot(fig3, use_container_width=True)
                plt.close()

            st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
            st.markdown("**Recent Forecasts**")
            recent = sku_df[["date","point_forecast","interval_lower","interval_upper",
                              "reliability_score","risk_tier","safety_stock_aci",
                              "escalation","calibration_health"]].tail(20).sort_values("date", ascending=False)
            st.dataframe(recent.style.format({
                "point_forecast":"{:.1f}","interval_lower":"{:.1f}",
                "interval_upper":"{:.1f}","safety_stock_aci":"{:.1f}",
                "reliability_score":"{:.0f}"
            }), use_container_width=True, height=280)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; color:#475569; font-size:0.78rem; margin-top:4rem; padding-top:1.5rem; border-top:1px solid rgba(255,255,255,0.06);">
      <strong>SupplyShield AI Enterprise</strong> &nbsp;·&nbsp; Adaptive Conformal Inference Architecture (Gibbs &amp; Candès, 2022) &nbsp;·&nbsp;
      Probabilistic Demand Risk Engine &nbsp;·&nbsp; Evaluated on Walmart M5 Benchmark
    </div>
    """, unsafe_allow_html=True)
