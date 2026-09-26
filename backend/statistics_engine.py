import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def descriptive(df, col):
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if len(s) == 0:
        return {}
    q1, q3 = s.quantile(.25), s.quantile(.75)
    return {
        "count": int(s.count()), "mean": float(s.mean()), "median": float(s.median()),
        "std": float(s.std()), "variance": float(s.var()), "min": float(s.min()),
        "q1": float(q1), "q3": float(q3), "max": float(s.max()),
        "iqr": float(q3-q1), "skewness": float(s.skew()), "kurtosis": float(s.kurtosis())
    }

def zscore_outliers(df, col):
    s = pd.to_numeric(df[col], errors="coerce")
    z = stats.zscore(s.dropna())
    return int(np.sum(np.abs(z) > 3)), z

def correlation(df, x, y):
    d = df[[x,y]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(d) < 3:
        return None
    pearson_r, p = stats.pearsonr(d[x], d[y])
    spearman_r, sp = stats.spearmanr(d[x], d[y])
    return {"pearson_r": float(pearson_r), "p_value": float(p),
            "spearman_r": float(spearman_r), "spearman_p": float(sp), "n": len(d)}

def regression(df, x, y):
    d = df[[x,y]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(d) < 5 or d[x].nunique() < 2:
        return None
    X, Y = d[[x]], d[y]
    model = LinearRegression().fit(X, Y)
    pred = model.predict(X)
    return {
        "slope": float(model.coef_[0]), "intercept": float(model.intercept_),
        "r2": float(r2_score(Y, pred)),
        "mae": float(mean_absolute_error(Y, pred)),
        "rmse": float(np.sqrt(mean_squared_error(Y, pred))),
        "n": len(d)
    }

def ttest_two_groups(df, category, metric):
    d = df[[category, metric]].copy()
    d[metric] = pd.to_numeric(d[metric], errors="coerce")
    groups = [g[metric].dropna().values for _, g in d.groupby(category)]
    labels = [str(x) for x in d.groupby(category).groups.keys()]
    if len(groups) != 2 or min(map(len, groups)) < 2:
        return None
    t, p = stats.ttest_ind(groups[0], groups[1], equal_var=False)
    return {"group_a": labels[0], "group_b": labels[1],
            "t_stat": float(t), "p_value": float(p),
            "mean_a": float(np.mean(groups[0])), "mean_b": float(np.mean(groups[1]))}

def chi_square(df, a, b):
    table = pd.crosstab(df[a], df[b])
    if table.shape[0] < 2 or table.shape[1] < 2:
        return None
    chi, p, dof, _ = stats.chi2_contingency(table)
    return {"chi2": float(chi), "p_value": float(p), "dof": int(dof)}

def numeric_summary(df, max_cols=12):
    out = {}
    for c in df.select_dtypes(include=np.number).columns[:max_cols]:
        out[c] = descriptive(df, c)
    return out
