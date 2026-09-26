import streamlit as st
import numpy as np
from backend.statistics_engine import descriptive, correlation, regression, ttest_two_groups, chi_square
from backend.data_engine import profile

def render_statistics():
    df=st.session_state.data
    p=profile(df)
    st.title("📐 Statistical Analysis")
    nums=p["numeric"]; cats=p["categorical"]
    if not nums:
        st.warning("No numeric columns were detected.")
        return

    col=st.selectbox("Numeric variable",nums)
    d=descriptive(df,col)
    st.subheader(f"Descriptive statistics — {col}")
    cols=st.columns(5)
    for c,(k,v) in zip(cols, list(d.items())[:5]): c.metric(k.replace("_"," ").title(),f"{v:,.3f}" if isinstance(v,float) else f"{v:,}")
    cols=st.columns(5)
    for c,(k,v) in zip(cols, list(d.items())[5:10]): c.metric(k.replace("_"," ").title(),f"{v:,.3f}" if isinstance(v,float) else f"{v:,}")

    with st.expander("💡 Explain This statistic"):
        st.write("Mean is the arithmetic average. Median is the middle observation. Standard deviation measures spread. IQR is the middle 50% range. Skewness describes asymmetry.")

    if len(nums)>=2:
        st.subheader("Relationship / regression")
        x,y=st.columns(2)
        xcol=x.selectbox("Predictor",nums,index=0)
        ycol=y.selectbox("Target",nums,index=1)
        cr=correlation(df,xcol,ycol); rg=regression(df,xcol,ycol)
        if cr:
            a,b,c,d=st.columns(4)
            a.metric("Pearson r",f"{cr['pearson_r']:.4f}")
            b.metric("Pearson p-value",f"{cr['p_value']:.5g}")
            c.metric("Spearman r",f"{cr['spearman_r']:.4f}")
            d.metric("Sample size",f"{cr['n']:,}")
        if rg:
            a,b,c,d=st.columns(4)
            a.metric("R²",f"{rg['r2']:.4f}")
            b.metric("Slope",f"{rg['slope']:.4f}")
            c.metric("MAE",f"{rg['mae']:.4f}")
            d.metric("RMSE",f"{rg['rmse']:.4f}")
        with st.expander("💡 Explain This relationship"):
            st.write("A p-value is evidence against the null hypothesis under the test assumptions; it is not the probability that the hypothesis is true. R² describes the share of variation explained by a linear regression model in this sample. Neither establishes causation.")

    if cats:
        st.subheader("Categorical significance tests")
        cat=st.selectbox("Category",cats)
        if df[cat].nunique(dropna=True)==2:
            res=ttest_two_groups(df,cat,col)
            if res:
                a,b,c=st.columns(3)
                a.metric("t-statistic",f"{res['t_stat']:.4f}")
                b.metric("p-value",f"{res['p_value']:.5g}")
                c.metric("Group means",f"{res['mean_a']:.2f} vs {res['mean_b']:.2f}")
        if len(cats)>=2:
            cat2=st.selectbox("Second category",cats,index=min(1,len(cats)-1))
            res=chi_square(df,cat,cat2)
            if res:
                a,b,c=st.columns(3)
                a.metric("Chi-square",f"{res['chi2']:.3f}")
                b.metric("p-value",f"{res['p_value']:.5g}")
                c.metric("Degrees of freedom",res["dof"])
