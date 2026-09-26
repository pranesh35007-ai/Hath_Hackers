# Hath_Hackers — Enterprise AI Data Analyst

A Streamlit-based AI data analysis application designed for CSV/XLSX business datasets.

## Included
- Role-based login: Admin / Analyst / Viewer
- CSV and Excel upload
- Executive KPI dashboard
- Interactive gradient-style Plotly charts
- Data quality assessment
- Descriptive statistics
- Correlation, regression and hypothesis testing where appropriate
- Outlier and anomaly detection
- Basic forecasting
- Segmentation
- AI-generated executive insights
- AI-generated recommendations
- Ask AI with suggested questions
- Explain This for charts/statistics
- PDF executive report

## Run locally

### 1. Create environment
Windows:
```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. Add Gemini key
Copy `.env.example` to `.env` and set:
```text
GEMINI_API_KEY=your_key
```

### 4. Run
```bash
streamlit run app.py
```

## Demo role credentials

The default passwords are read from environment variables. For a quick local demo, the fallback values are:
- Admin: `admin123`
- Analyst: `analyst123`
- Viewer: `viewer123`

Change them before real deployment.

## Production notes
- Put secrets in Streamlit Secrets or your deployment secret manager.
- Replace demo authentication with enterprise SSO/OAuth for real production.
- Never commit `.env` or API keys to Git.
- AI receives statistical summaries and sampled data, not arbitrary code execution.
