import streamlit as st
from backend.ai_agent import ask_ai, suggested_questions

def render_ask_ai():
    st.title("🤖 Ask AI")
    st.caption("Ask questions in normal language. The agent uses the uploaded dataset and analytical context.")

    qs=suggested_questions(st.session_state.data)
    st.markdown("### Suggested questions")
    for i in range(0,len(qs),2):
        cols=st.columns(2)
        for j in range(2):
            if i+j<len(qs):
                if cols[j].button(qs[i+j],key=f"q{i+j}",use_container_width=True):
                    st.session_state.ai_question=qs[i+j]

    q=st.text_area("Your question",value=st.session_state.get("ai_question",""),
                   placeholder="Example: Which category is underperforming and what evidence supports that?")
    if st.button("Ask Hath_Hackers AI",type="primary",use_container_width=True):
        if not q.strip():
            st.warning("Enter a question or choose a suggested question.")
            return
        with st.spinner("Analyzing the data and preparing the answer..."):
            answer=ask_ai(st.session_state.data,q)
        st.session_state.ai_history=st.session_state.get("ai_history",[])+[(q,answer)]
    for q,a in reversed(st.session_state.get("ai_history",[])):
        st.markdown(f"#### ❓ {q}")
        st.markdown(a)
        st.divider()
