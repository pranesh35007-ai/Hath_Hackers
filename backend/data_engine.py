import io
import pandas as pd
import numpy as np

def load_uploaded_file(uploaded_file):
    data = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(data))
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(data))
    else:
        raise ValueError("Only CSV and Excel files are supported.")
    df = clean_basic(df)
    if df.empty:
        raise ValueError("The uploaded dataset has no rows.")
    return df, uploaded_file.name

def clean_basic(df):
    df = df.copy()
    df.columns = [
        str(c).strip().replace("\n", " ").replace("  ", " ")
        for c in df.columns
    ]
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    for c in df.columns:
        if df[c].dtype == "object":
            stripped = df[c].astype(str).str.strip()
            converted = pd.to_numeric(stripped.str.replace(",", "", regex=False), errors="coerce")
            if converted.notna().mean() >= 0.85:
                df[c] = converted
            else:
                dt = pd.to_datetime(stripped, errors="coerce")
                if dt.notna().mean() >= 0.90:
                    df[c] = dt
                else:
                    df[c] = stripped.replace({"nan": np.nan, "None": np.nan})
    return df

def profile(df):
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    dates = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
    missing = int(df.isna().sum().sum())
    duplicate = int(df.duplicated().sum())
    return {
        "rows": len(df), "columns": len(df.columns), "numeric": numeric,
        "categorical": categorical, "dates": dates, "missing": missing,
        "duplicate": duplicate
    }

def likely_measure(df):
    nums = df.select_dtypes(include=np.number)
    if nums.empty:
        return None
    candidates = []
    for c in nums.columns:
        if nums[c].nunique(dropna=True) > 1:
            score = nums[c].nunique(dropna=True)
            name = c.lower()
            if any(k in name for k in ["id", "code", "zip", "phone"]):
                score -= 100000
            if any(k in name for k in ["sales", "revenue", "profit", "amount", "price", "score", "value", "income", "cost"]):
                score += 10000
            candidates.append((score, c))
    return max(candidates)[1] if candidates else nums.columns[0]
