import streamlit as st
from backend.data_engine import profile

def render_data_preview():
    df=st.session_state.data
    st.title("🗂 Data Preview")
    p=profile(df)
    c1,c2,c3=st.columns(3)
    c1.metric("Rows",f"{p['rows']:,}")
    c2.metric("Columns",f"{p['columns']:,}")
    c3.metric("Numeric fields",f"{len(p['numeric']):,}")
    st.dataframe(df.head(100),use_container_width=True,height=500)
    st.download_button("⬇️ Download processed CSV",df.to_csv(index=False).encode("utf-8"),
                       "hath_hackers_processed.csv","text/csv")
