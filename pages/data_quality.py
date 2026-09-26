import streamlit as st
import pandas as pd
import numpy as np

def render_data_quality():
    df=st.session_state.data
    st.title("🧹 Data Quality Center")
    total=df.size
    missing=int(df.isna().sum().sum())
    duplicate=int(df.duplicated().sum())
    completeness=100*(1-missing/max(total,1))
    score=max(0,round(completeness - min(20,duplicate/max(len(df),1)*100),1))
    a,b,c=st.columns(3)
    a.metric("Quality score",f"{score}/100")
    b.metric("Missing cells",f"{missing:,}")
    c.metric("Duplicate rows",f"{duplicate:,}")

    q=pd.DataFrame({
        "Column":df.columns,
        "Data type":[str(df[c].dtype) for c in df.columns],
        "Missing":[int(df[c].isna().sum()) for c in df.columns],
        "Missing %":[round(df[c].isna().mean()*100,2) for c in df.columns],
        "Unique":[int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    st.dataframe(q,use_container_width=True)
    st.caption("The quality score is a screening metric, not a formal data-governance certification.")
