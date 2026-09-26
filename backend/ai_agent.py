import json
import os
import time

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.data_engine import profile, likely_measure
from backend.statistics_engine import numeric_summary, correlation, regression, descriptive

# Load .env here so the AI module works even when Streamlit imports it directly.
load_dotenv()


DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
]


def _client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    return genai.Client(api_key=key)


def _model_candidates():
    """Return the configured model followed by safe fallbacks."""
    primary = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
    configured = os.getenv("GEMINI_FALLBACK_MODELS", "")
    fallbacks = [m.strip() for m in configured.split(",") if m.strip()]

    # Keep defaults after any user-configured fallbacks.
    models = [primary, *fallbacks, *DEFAULT_FALLBACK_MODELS]
    return list(dict.fromkeys(m for m in models if m))


def _is_retryable_error(exc):
    """503/429/5xx errors are usually temporary service/rate-limit errors."""
    msg = str(exc).upper()
    retry_codes = ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "502", "504")
    return any(code in msg for code in retry_codes)


def _generate(client, prompt):
    """Generate text with retry + model fallback so temporary Gemini outages don't break the app."""
    last_error = None

    for model in _model_candidates():
        # Exponential backoff for transient errors, as recommended by Google's Gemini API docs.
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.15),
                )
                if response and response.text:
                    return response.text
                raise RuntimeError(f"Gemini returned an empty response from {model}.")
            except Exception as exc:
                last_error = exc
                if not _is_retryable_error(exc) or attempt == 2:
                    break
                time.sleep(2 ** attempt)

        # If the current model is unavailable, try the next model.
        if last_error is not None and _is_retryable_error(last_error):
            continue
        break

    raise last_error or RuntimeError("Gemini request failed.")


def _safe_sample(df, n=40):
    return df.head(n).copy()


def build_context(df):
    p = profile(df)
    measure = likely_measure(df)
    ctx = {
        "profile": p,
        "likely_primary_measure": measure,
        "numeric_summary": numeric_summary(df),
        "sample": _safe_sample(df).to_dict(orient="records"),
        "columns": [
            {"name": c, "dtype": str(df[c].dtype), "unique": int(df[c].nunique(dropna=True))}
            for c in df.columns
        ],
    }
    return ctx


def ask_ai(df, question, mode="answer"):
    client = _client()
    ctx = build_context(df)
    if client is None:
        return "Gemini API key is not configured. Add GEMINI_API_KEY to .env or Streamlit Secrets."

    system = """
You are Hath_Hackers Enterprise AI Data Analyst. Analyze only the supplied dataset context.
Act as a senior data analyst, statistician, business analyst and reporting analyst.
Never invent a value. If the dataset does not support a conclusion, say so.
Use plain English for non-technical stakeholders. Separate observed facts, statistical evidence,
interpretation and recommendation. Correlation is not causation. Explain p-values carefully.
When useful, recommend a next analytical step.
Return concise, structured Markdown.
"""
    prompt = f"""{system}

DATASET CONTEXT:
{json.dumps(ctx, default=str)[:45000]}

USER QUESTION:
{question}

Provide:
1. Direct answer
2. Evidence from the data
3. Relevant statistical interpretation
4. Business meaning
5. Recommendation or next step
"""

    try:
        return _generate(client, prompt)
    except Exception as exc:
        return (
            "AI service is temporarily unavailable. "
            "The app automatically retried the request and tried the configured fallback models. "
            f"Last error: {exc}"
        )


def executive_insights(df):
    client = _client()
    ctx = build_context(df)
    if client is None:
        return "Gemini API key is not configured. Add GEMINI_API_KEY to enable AI insights."

    prompt = f"""
You are producing an executive business report from this dataset.
Do not invent facts. Identify the most decision-relevant trends, concentrations, outliers,
relationships and data-quality limitations.

Dataset:
{json.dumps(ctx, default=str)[:45000]}

Return:
### Executive Summary
3-6 sentences.

### Key Findings
5 bullets with actual values where available.

### Business Implications
3-5 bullets.

### Recommendations
3-5 specific, evidence-linked actions.

### Caveats
Important limitations or data gaps.
"""

    try:
        return _generate(client, prompt)
    except Exception as exc:
        return (
            "AI service is temporarily unavailable. "
            "The app automatically retried the request and tried the configured fallback models. "
            f"Last error: {exc}"
        )


def suggested_questions(df):
    p = profile(df)
    nums = p["numeric"]
    cats = p["categorical"]
    dates = p["dates"]
    q = []
    if nums:
        q += [
            f"What are the most important insights about {nums[0]}?",
            f"Which records or categories have the highest {nums[0]}?",
        ]
    if cats and nums:
        q += [
            f"Which {cats[0]} performs best and why?",
            f"Compare {nums[0]} across {cats[0]}.",
        ]
    if len(nums) >= 2:
        q += [
            f"What is the relationship between {nums[0]} and {nums[1]}?",
            f"Is the relationship between {nums[0]} and {nums[1]} statistically significant?",
        ]
    if dates and nums:
        q += [
            f"What trend can you identify in {nums[0]} over time?",
            f"Are there unusual periods or anomalies in {nums[0]}?",
        ]
    q += [
        "What should management investigate first?",
        "What are the biggest data-quality risks?",
        "Give me a non-technical executive summary.",
    ]
    return list(dict.fromkeys(q))[:8]


# Backward compatibility: older pages may import this spelling.
execute_insights = executive_insights
