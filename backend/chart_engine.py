import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = ["#1769AA","#0F8B8D","#D6A84F","#6B5CA5","#D05A47","#2C7A7B","#4E79A7","#59A14F"]

def base(fig):
    fig.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial", color="#152238"),
        margin=dict(l=20,r=20,t=60,b=30), legend_title_text=""
    )
    return fig

def auto_charts(df):
    charts = []
    nums = df.select_dtypes(include=np.number).columns.tolist()
    cats = df.select_dtypes(include=["object","category","bool"]).columns.tolist()
    dates = df.select_dtypes(include=["datetime64[ns]","datetime64[ns, UTC]"]).columns.tolist()

    if dates and nums:
        d = df[[dates[0], nums[0]]].dropna().sort_values(dates[0])
        d = d.groupby(dates[0], as_index=False)[nums[0]].sum()
        fig = px.line(d, x=dates[0], y=nums[0], markers=True, title=f"{nums[0]} over time")
        fig.update_traces(line=dict(width=3), marker=dict(size=7))
        fig.update_layout(hovermode="x unified")
        charts.append(("Trend", base(fig)))

    if cats and nums:
        c, n = cats[0], nums[0]
        d = df[[c,n]].dropna().groupby(c, as_index=False)[n].sum().sort_values(n, ascending=False).head(12)
        fig = px.bar(d, x=c, y=n, text_auto=".2s", title=f"{n} by {c}", color=n,
                     color_continuous_scale=["#DCEAF7","#1769AA","#0F8B8D"])
        fig.update_traces(textposition="outside")
        charts.append(("Performance", base(fig)))

    if len(nums) >= 2:
        x,y = nums[0],nums[1]
        d=df[[x,y]].dropna()
        fig=px.scatter(d,x=x,y=y,title=f"{y} vs {x}",trendline="ols",
                       color_discrete_sequence=["#1769AA"])
        charts.append(("Relationship", base(fig)))

    if nums:
        n=nums[0]
        fig=px.histogram(df,x=n,nbins=30,title=f"Distribution of {n}",
                         color_discrete_sequence=["#0F8B8D"])
        charts.append(("Distribution", base(fig)))

    if len(nums) >= 2:
        corr=df[nums].corr(numeric_only=True)
        fig=px.imshow(corr,text_auto=".2f",aspect="auto",title="Correlation heatmap",
                      color_continuous_scale=["#F4F7FB","#1769AA","#10243E"])
        charts.append(("Correlation", base(fig)))

    return charts
