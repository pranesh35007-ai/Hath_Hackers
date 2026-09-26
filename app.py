import streamlit as st
from backend.data_engine import load_uploaded_file
from frontend.styles import apply_theme
from pages.dashboard import render_dashboard
from pages.data_preview import render_data_preview
from pages.data_quality import render_data_quality
from pages.statistics import render_statistics
from pages.insights import render_insights
from pages.ask_ai import render_ask_ai
from pages.reports import render_reports

st.set_page_config(
    page_title="Hath_Hackers | AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_theme()

uploaded = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx", "xls"],
    help="Upload a business dataset to activate the AI analysis engine."
)

if uploaded is not None:
    try:
        st.session_state.data, st.session_state.dataset_name = load_uploaded_file(uploaded)
        st.session_state.analysis_ready = True
    except Exception as e:
        st.sidebar.error(f"Could not read file: {e}")
else:
    st.sidebar.info("Upload a CSV/XLSX file to begin.")

if st.sidebar.button("🔄 Reset session"):
    for key in ["data", "dataset_name", "analysis_ready", "ai_history"]:
        st.session_state.pop(key, None)
    st.rerun()

if "data" not in st.session_state:
    st.title("📊 Hath_Hackers")
    st.subheader("Enterprise AI Data Analysis Agent")
    st.markdown("""
    Upload a **CSV or Excel file** and turn raw data into an executive-ready analysis.

    **What the platform does**
    - Automatically understands the dataset
    - Builds KPI cards and professional interactive charts
    - Performs statistical and predictive analysis where appropriate
    - Detects data-quality issues, outliers and anomalies
    - Generates plain-English insights and recommendations
    - Lets users ask the AI questions about the actual dataset
    - Exports a PDF executive report
    """)
    st.info("👈 Start by uploading a CSV or Excel file from the sidebar.")
    st.stop()

pages = {
    "📊 Executive Dashboard": render_dashboard,
    "🗂 Data Preview": render_data_preview,
    "🧹 Data Quality": render_data_quality,
    "📐 Statistics": render_statistics,
    "💡 AI Insights": render_insights,
    "🤖 Ask AI": render_ask_ai,
    "📄 PDF Report": render_reports,
}

selection = st.sidebar.radio("Navigate", list(pages.keys()))
pages[selection]()
