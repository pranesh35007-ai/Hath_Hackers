import streamlit as st
import numpy as np
from backend.data_engine import profile, likely_measure
from backend.chart_engine import auto_charts
from backend.advanced import anomaly_report

def fmt(x):
    if x is None: return "—"
    if abs(x)>=1_000_000: return f"{x/1_000_000:.2f}M"
    if abs(x)>=1_000: return f"{x/1_000:.1f}K"
    return f"{x:,.2f}" if isinstance(x,float) else f"{x:,}"

def render_dashboard():
    df=st.session_state.data
    p=profile(df)
    st.title("Executive Dashboard")
    st.caption(f"Dataset: **{st.session_state.dataset_name}** · {p['rows']:,} rows · {p['columns']} columns")

    nums=p["numeric"]; measure=likely_measure(df)
    cards=[
        ("Rows",fmt(p["rows"]),"Dataset volume"),
        ("Columns",fmt(p["columns"]),"Available fields"),
        ("Missing cells",fmt(p["missing"]),"Quality signal"),
        ("Duplicates",fmt(p["duplicate"]),"Potential duplicate rows"),
    ]
    if measure:
        s=df[measure].dropna()
        cards += [(f"Primary KPI · {measure}",fmt(float(s.sum())),"Total"),
                  (f"Average · {measure}",fmt(float(s.mean())),"Mean"),
                  (f"Median · {measure}",fmt(float(s.median())),"Median")]
    cols=st.columns(min(len(cards),4))
    for i,(a,b,c) in enumerate(cards):
        with cols[i%len(cols)]:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{a}</div><div class="kpi-value">{b}</div><div class="kpi-note">{c}</div></div>',unsafe_allow_html=True)
        if (i+1)%4==0 and i+1<len(cards): cols=st.columns(4)

    st.markdown("### 📈 Auto-generated analysis")
    charts=auto_charts(df)
    for i in range(0,len(charts),2):
        cc=st.columns(2)
        for j in range(2):
            if i+j<len(charts):
                name,fig=charts[i+j]
                with cc[j]:
                    st.plotly_chart(fig,use_container_width=True)
                    with st.expander(f"💡 Explain This — {name}"):
                        st.write("This chart is automatically selected from the dataset structure. Use the AI Insights or Ask AI tabs for dataset-specific interpretation.")

    an=anomaly_report(df)
    if an:
        st.markdown("### 🚨 Anomaly monitoring")
        st.info(f"Isolation Forest flagged **{an['anomalies']}** potentially unusual observations across {len(an['features'])} numeric features. This is an investigation signal, not proof of an error or fraud.")
