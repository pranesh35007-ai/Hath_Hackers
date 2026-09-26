import streamlit as st
from backend.ai_agent import executive_insights
from backend.advanced import anomaly_report, segmentation

def render_insights():
    st.title("💡 AI Insights & Recommendations")
    df=st.session_state.data
    if st.button("Generate / refresh AI executive analysis",type="primary"):
        with st.spinner("AI is analyzing the dataset..."):
            st.session_state.ai_insights=executive_insights(df)
    text=st.session_state.get("ai_insights")
    if text:
        st.markdown(text)
    else:
        st.info("Click the button to generate an evidence-linked executive analysis.")

    st.markdown("### 🔎 Analytical signals")
    an=anomaly_report(df)
    seg=segmentation(df)
    a,b=st.columns(2)
    with a:
        if an:
            st.metric("Potential anomalies",an["anomalies"])
            st.caption("Screening signal generated from numeric features.")
        else: st.info("Not enough numeric data for anomaly screening.")
    with b:
        if seg:
            st.metric("Suggested segments",seg["clusters"])
            st.caption(f"Based on: {', '.join(seg['features'])}")
        else: st.info("Not enough numeric data for segmentation.")
