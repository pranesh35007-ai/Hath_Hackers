import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def anomaly_report(df, max_features=8):
    nums=df.select_dtypes(include=np.number).columns.tolist()[:max_features]
    if len(nums)<1 or len(df)<10: return None
    d=df[nums].dropna()
    if len(d)<10: return None
    model=IsolationForest(contamination="auto", random_state=42)
    labels=model.fit_predict(StandardScaler().fit_transform(d))
    return {"features":nums,"anomalies":int((labels==-1).sum()),"rows_analyzed":len(d)}

def segmentation(df):
    nums=df.select_dtypes(include=np.number).columns.tolist()
    if len(nums)<2 or len(df)<20: return None
    cols=nums[:5]
    d=df[cols].dropna()
    if len(d)<20: return None
    x=StandardScaler().fit_transform(d)
    k=min(4,max(2,int(np.sqrt(len(d)/20))+2))
    labels=KMeans(n_clusters=k,random_state=42,n_init=10).fit_predict(x)
    return {"clusters":int(k),"features":cols,"sizes":pd.Series(labels).value_counts().sort_index().tolist()}
