import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    :root {
      --navy:#10243E;
      --blue:#1769AA;
      --teal:#0F8B8D;
      --gold:#D6A84F;
      --ink:#152238;
      --muted:#617083;
      --panel:#FFFFFF;
      --bg:#F4F7FB;
    }
    .stApp { background:var(--bg); color:var(--ink); }
    [data-testid="stSidebar"] {
      background:linear-gradient(180deg,#10243E 0%,#173A5E 55%,#0F5B68 100%);
    }
    [data-testid="stSidebar"] * { color:#F8FAFC !important; }
    .block-container { padding-top:1.6rem; }
    .kpi {
      background:var(--panel); border:1px solid #E4EAF2; border-radius:16px;
      padding:18px; box-shadow:0 7px 22px rgba(16,36,62,.07);
      min-height:125px;
    }
    .kpi-label { font-size:.82rem; color:var(--muted); font-weight:700; text-transform:uppercase; }
    .kpi-value { font-size:1.8rem; font-weight:800; color:var(--navy); margin-top:7px; }
    .kpi-note { font-size:.82rem; color:var(--teal); margin-top:4px; }
    .section-title { font-size:1.25rem; font-weight:800; color:var(--navy); margin-top:1rem; }
    .insight {
      background:white; border-left:5px solid var(--blue); padding:14px 18px;
      border-radius:10px; box-shadow:0 4px 15px rgba(16,36,62,.05); margin-bottom:10px;
    }
    .login-card {
      max-width:720px; margin:5rem auto 1.5rem; padding:35px; border-radius:22px;
      background:linear-gradient(135deg,#10243E,#1769AA); color:white;
      box-shadow:0 18px 50px rgba(16,36,62,.18);
    }
    .login-brand { letter-spacing:3px; font-weight:900; font-size:.85rem; opacity:.8; }
    .small-muted { color:var(--muted); font-size:.9rem; }
    </style>
    """, unsafe_allow_html=True)
