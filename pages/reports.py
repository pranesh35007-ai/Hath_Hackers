import io
import os
import datetime
import tempfile

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.enums import TA_CENTER

from backend.data_engine import profile, likely_measure
from backend.statistics_engine import descriptive
from backend.ai_agent import executive_insights


# ============================================================
# PDF COLORS
# ============================================================

NAVY = "#10243E"
BLUE = "#1769AA"
LIGHT_BLUE = "#EAF4FB"
RED = "#D62828"
GRAY = "#667085"
LIGHT_GRAY = "#D8E0EA"


# ============================================================
# SAFE TEXT FOR REPORTLAB
# ============================================================

def safe_text(value):
    """Make values safe for ReportLab Paragraph."""
    if value is None:
        return ""

    text = str(value)

    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ============================================================
# CREATE CHART IMAGE
# ============================================================

def save_chart(fig):
    """
    Convert matplotlib figure into a temporary PNG file.
    Returns the file path.
    """
    temp = tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False
    )

    fig.savefig(
        temp.name,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close(fig)

    return temp.name


# ============================================================
# NUMERIC DISTRIBUTION CHART
# ============================================================

def create_distribution_chart(df, column):
    data = pd.to_numeric(df[column], errors="coerce").dropna()

    if data.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.hist(
        data,
        bins=20,
        edgecolor="white"
    )

    ax.set_title(
        f"Distribution of {column}",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")

    ax.grid(
        axis="y",
        alpha=0.2
    )

    fig.tight_layout()

    return save_chart(fig)


# ============================================================
# CATEGORY BAR CHART
# ============================================================

def create_category_chart(df, column):
    data = df[column].dropna()

    if data.empty:
        return None

    counts = data.astype(str).value_counts().head(10)

    if counts.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 4.5))

    counts.sort_values().plot(
        kind="barh",
        ax=ax
    )

    ax.set_title(
        f"Top Categories — {column}",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel("Count")
    ax.set_ylabel(column)

    ax.grid(
        axis="x",
        alpha=0.2
    )

    fig.tight_layout()

    return save_chart(fig)


# ============================================================
# TIME TREND CHART
# ============================================================

def create_trend_chart(df):
    date_column = None

    # First look for actual datetime columns
    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            date_column = column
            break

    # If no datetime column exists, try converting object columns
    if date_column is None:
        for column in df.columns:
            if df[column].dtype == "object":
                converted = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                if converted.notna().mean() >= 0.7:
                    date_column = column
                    break

    if date_column is None:
        return None

    measure = likely_measure(df)

    if not measure:
        return None

    temp = pd.DataFrame({
        "date": pd.to_datetime(
            df[date_column],
            errors="coerce"
        ),
        "value": pd.to_numeric(
            df[measure],
            errors="coerce"
        )
    }).dropna()

    if temp.empty:
        return None

    temp = (
        temp
        .groupby("date")["value"]
        .sum()
        .sort_index()
    )

    if len(temp) < 2:
        return None

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(
        temp.index,
        temp.values,
        marker="o",
        linewidth=2
    )

    ax.set_title(
        f"{measure} Trend Over Time",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel(date_column)
    ax.set_ylabel(measure)

    ax.grid(
        alpha=0.2
    )

    fig.autofmt_xdate()
    fig.tight_layout()

    return save_chart(fig)


# ============================================================
# CORRELATION HEATMAP
# ============================================================

def create_correlation_chart(df):
    numeric_df = df.select_dtypes(
        include=np.number
    )

    if numeric_df.shape[1] < 2:
        return None

    # Limit to avoid creating an unreadable huge chart
    numeric_df = numeric_df.iloc[:, :10]

    corr = numeric_df.corr()

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    image = ax.imshow(
        corr.values,
        aspect="auto"
    )

    ax.set_xticks(
        range(len(corr.columns))
    )

    ax.set_yticks(
        range(len(corr.columns))
    )

    ax.set_xticklabels(
        corr.columns,
        rotation=45,
        ha="right"
    )

    ax.set_yticklabels(
        corr.columns
    )

    # Add correlation values
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            value = corr.iloc[i, j]

            ax.text(
                j,
                i,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=8
            )

    ax.set_title(
        "Correlation Heatmap",
        fontsize=14,
        fontweight="bold"
    )

    fig.colorbar(
        image,
        ax=ax,
        fraction=0.046,
        pad=0.04
    )

    fig.tight_layout()

    return save_chart(fig)


# ============================================================
# SCATTER PLOT
# ============================================================

def create_scatter_chart(df):
    numeric_columns = list(
        df.select_dtypes(
            include=np.number
        ).columns
    )

    if len(numeric_columns) < 2:
        return None

    x_col = numeric_columns[0]
    y_col = numeric_columns[1]

    temp = df[
        [x_col, y_col]
    ].copy()

    temp[x_col] = pd.to_numeric(
        temp[x_col],
        errors="coerce"
    )

    temp[y_col] = pd.to_numeric(
        temp[y_col],
        errors="coerce"
    )

    temp = temp.dropna()

    if len(temp) < 2:
        return None

    fig, ax = plt.subplots(
        figsize=(8, 4.5)
    )

    ax.scatter(
        temp[x_col],
        temp[y_col],
        alpha=0.65
    )

    ax.set_title(
        f"{y_col} vs {x_col}",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)

    ax.grid(
        alpha=0.2
    )

    fig.tight_layout()

    return save_chart(fig)


# ============================================================
# GENERATE ALL CHARTS
# ============================================================

def generate_report_charts(df):
    charts = []

    numeric_columns = list(
        df.select_dtypes(
            include=np.number
        ).columns
    )

    categorical_columns = list(
        df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns
    )

    # 1. Main numeric distribution
    if numeric_columns:
        path = create_distribution_chart(
            df,
            numeric_columns[0]
        )

        if path:
            charts.append(
                ("Numeric Distribution", path)
            )

    # 2. Category chart
    if categorical_columns:
        path = create_category_chart(
            df,
            categorical_columns[0]
        )

        if path:
            charts.append(
                ("Category Analysis", path)
            )

    # 3. Trend chart
    path = create_trend_chart(df)

    if path:
        charts.append(
            ("Trend Analysis", path)
        )

    # 4. Correlation
    path = create_correlation_chart(df)

    if path:
        charts.append(
            ("Correlation Analysis", path)
        )

    # 5. Scatter
    path = create_scatter_chart(df)

    if path:
        charts.append(
            ("Relationship Analysis", path)
        )

    return charts


# ============================================================
# KPI DASHBOARD TABLE
# ============================================================

def create_kpi_table(df):
    p = profile(df)

    numeric_columns = len(
        df.select_dtypes(
            include=np.number
        ).columns
    )

    categorical_columns = len(
        df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns
    )

    return [
        [
            "Rows",
            f"{p['rows']:,}",
            "Columns",
            f"{p['columns']:,}"
        ],
        [
            "Missing Cells",
            f"{p['missing']:,}",
            "Duplicate Rows",
            f"{p['duplicate']:,}"
        ],
        [
            "Numeric Columns",
            f"{numeric_columns:,}",
            "Categorical Columns",
            f"{categorical_columns:,}"
        ],
    ]


# ============================================================
# STATISTICS TABLE
# ============================================================

def create_statistics_table(df):
    measure = likely_measure(df)

    if not measure:
        return None, None

    d = descriptive(
        df,
        measure
    )

    rows = [
        ["Statistic", "Value"]
    ]

    for key, value in d.items():

        if isinstance(
            value,
            (float, np.floating)
        ):
            value_text = f"{float(value):.4f}"
        else:
            value_text = str(value)

        rows.append(
            [
                key.replace(
                    "_",
                    " "
                ).title(),
                value_text
            ]
        )

    return measure, rows


# ============================================================
# PDF GENERATOR
# ============================================================

def make_pdf(df, filename):

    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        textColor=colors.HexColor(NAVY),
        alignment=TA_CENTER,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor(GRAY),
        alignment=TA_CENTER,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=15,
        leading=20,
        textColor=colors.HexColor(BLUE),
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor(GRAY)
    )

    story = []

    # ========================================================
    # COVER / TITLE
    # ========================================================

    story.append(
        Paragraph(
            "Hath_Hackers",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI DATA ANALYST",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Executive Data Analysis Report",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Dataset:</b> {safe_text(filename)}",
            body_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Generated:</b> "
            f"{datetime.datetime.now():%Y-%m-%d %H:%M}",
            body_style
        )
    )

    story.append(Spacer(1, 15))

    # ========================================================
    # EXECUTIVE DASHBOARD
    # ========================================================

    story.append(
        Paragraph(
            "📊 Executive Dashboard",
            heading_style
        )
    )

    kpi_data = create_kpi_table(df)

    kpi_table = Table(
        kpi_data,
        colWidths=[
            100,
            80,
            100,
            80
        ]
    )

    kpi_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor(LIGHT_BLUE)
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, -1),
                colors.HexColor(NAVY)
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica"
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (2, 0),
                (2, -1),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor(LIGHT_GRAY)
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "ALIGN",
                (1, 0),
                (1, -1),
                "CENTER"
            ),
            (
                "ALIGN",
                (3, 0),
                (3, -1),
                "CENTER"
            ),
        ])
    )

    story.append(kpi_table)

    story.append(Spacer(1, 12))

    # ========================================================
    # DATASET OVERVIEW
    # ========================================================

    p = profile(df)

    story.append(
        Paragraph(
            "🗂 Dataset Overview",
            heading_style
        )
    )

    overview_data = [
        ["Metric", "Value"],
        [
            "Rows",
            f"{p['rows']:,}"
        ],
        [
            "Columns",
            f"{p['columns']:,}"
        ],
        [
            "Missing Cells",
            f"{p['missing']:,}"
        ],
        [
            "Duplicate Rows",
            f"{p['duplicate']:,}"
        ],
    ]

    overview_table = Table(
        overview_data,
        colWidths=[220, 220]
    )

    overview_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(NAVY)
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor(LIGHT_GRAY)
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    story.append(overview_table)

    # ========================================================
    # CHARTS
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "📈 Visual Analytics",
            heading_style
        )
    )

    charts = generate_report_charts(df)

    if charts:

        for chart_title, chart_path in charts:

            story.append(
                Paragraph(
                    chart_title,
                    heading_style
                )
            )

            story.append(
                Image(
                    chart_path,
                    width=500,
                    height=280
                )
            )

            story.append(
                Spacer(1, 12)
            )

    else:

        story.append(
            Paragraph(
                "No suitable charts could be generated "
                "from this dataset.",
                body_style
            )
        )

    # ========================================================
    # STATISTICS
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "📐 Statistical Analysis",
            heading_style
        )
    )

    measure, stats_rows = create_statistics_table(df)

    if measure and stats_rows:

        story.append(
            Paragraph(
                f"Primary Measure: "
                f"<b>{safe_text(measure)}</b>",
                body_style
            )
        )

        stats_table = Table(
            stats_rows,
            colWidths=[220, 220]
        )

        stats_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(BLUE)
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(LIGHT_GRAY)
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
            ])
        )

        story.append(stats_table)

    else:

        story.append(
            Paragraph(
                "No primary numeric measure was detected "
                "for statistical analysis.",
                body_style
            )
        )

    # ========================================================
    # AI EXECUTIVE ANALYSIS
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "🤖 AI Executive Analysis",
            heading_style
        )
    )

    try:

        ai = executive_insights(df)

        for line in str(ai).splitlines():

            line = line.strip()

            if not line:
                continue

            # Markdown headings
            if line.startswith("### "):

                story.append(
                    Paragraph(
                        safe_text(
                            line.replace(
                                "### ",
                                ""
                            )
                        ),
                        heading_style
                    )
                )

            elif line.startswith("## "):

                story.append(
                    Paragraph(
                        safe_text(
                            line.replace(
                                "## ",
                                ""
                            )
                        ),
                        heading_style
                    )
                )

            else:

                # Remove markdown emphasis that ReportLab
                # doesn't understand reliably
                clean_line = (
                    line
                    .replace("**", "")
                    .replace("__", "")
                    .replace("*", "• ")
                )

                story.append(
                    Paragraph(
                        safe_text(clean_line),
                        body_style
                    )
                )

    except Exception as e:

        story.append(
            Paragraph(
                f"AI analysis could not be generated: "
                f"{safe_text(e)}",
                body_style
            )
        )

    # ========================================================
    # FOOTER
    # ========================================================

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Generated by Hath_Hackers AI Data Analyst",
            small_style
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(story)

    # Cleanup chart files
    for _, path in charts:
        try:
            os.remove(path)
        except Exception:
            pass

    return buf.getvalue()


# ============================================================
# STREAMLIT PAGE
# ============================================================

def render_reports():

    st.title("📄 Executive PDF Report")

    st.markdown(
        """
        Generate a management-ready PDF containing:

        - 📊 Executive KPI dashboard
        - 📈 Automatically generated charts
        - 📐 Statistical analysis
        - 🤖 AI executive insights
        - 💡 AI-driven recommendations
        """
    )

    if st.button(
        "🚀 Generate Complete PDF Report",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Generating dashboard, charts, statistics and AI analysis..."
        ):

            try:

                pdf = make_pdf(
                    st.session_state.data,
                    st.session_state.dataset_name
                )

                st.session_state.report_pdf = pdf

                st.success(
                    "✅ Executive report generated successfully!"
                )

            except Exception as e:

                st.error(
                    f"❌ Could not generate report: {e}"
                )

    if st.session_state.get("report_pdf"):

        st.download_button(
            "⬇️ Download Complete Executive PDF",
            st.session_state.report_pdf,
            "Hath_Hackers_Executive_Report.pdf",
            "application/pdf",
            use_container_width=True
        )
