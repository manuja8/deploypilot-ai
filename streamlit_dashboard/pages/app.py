from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import base64
import streamlit as st


# ============================================================
# PATHS
# ============================================================

DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = DASHBOARD_ROOT.parent

HISTORY_FILE = PROJECT_ROOT / "data" / "prediction_history.csv"

MODEL_1_METRICS_FILE = PROJECT_ROOT / "reports" / "metrics" / "model_1_metrics.txt"
MODEL_2_METRICS_FILE = PROJECT_ROOT / "reports" / "metrics" / "model_2_metrics.txt"

MODEL_1_CONFUSION_MATRIX = PROJECT_ROOT / "reports" / "figures" / "model_1_confusion_matrix.png"
MODEL_1_ROC_CURVE = PROJECT_ROOT / "reports" / "figures" / "model_1_roc_curve.png"
MODEL_2_CONFUSION_MATRIX = PROJECT_ROOT / "reports" / "figures" / "model_2_confusion_matrix.png"

API_BASE_URL = "http://127.0.0.1:8000"
PREDICT_URL = f"{API_BASE_URL}/predict"


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="DeployPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard Overview"

if "user_name" not in st.session_state:
    st.session_state.user_name = "DevOps Engineer"

# ============================================================
# Helper Function
# ============================================================


def get_base64_image(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        st.warning(f"Background image not found: {image_path}")
        return None

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    return encoded


# ============================================================
# CSS DESIGN SYSTEM
# ============================================================

def inject_css():
    bg_image_path = DASHBOARD_ROOT / "assets" / "login_bg.jpg"
    bg_image_base64 = get_base64_image(bg_image_path)

    css = """
        <style>
        :root {
            --bg-main: #f6f8fb;
            --bg-card: #ffffff;
            --bg-soft: #f8fafc;
            --bg-sidebar: #0f172a;
            --bg-sidebar-soft: #111c33;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --text-light: #e5e7eb;
            --primary: #2563eb;
            --primary-soft: #dbeafe;
            --green: #16a34a;
            --green-soft: #dcfce7;
            --red: #dc2626;
            --red-soft: #fee2e2;
            --yellow: #d97706;
            --yellow-soft: #fef3c7;
            --purple: #7c3aed;
            --purple-soft: #ede9fe;
            --border: #e2e8f0;
            --shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
            --shadow-soft: 0 10px 24px rgba(15, 23, 42, 0.06);
            --radius-lg: 22px;
            --radius-md: 16px;
            --radius-sm: 12px;
        }

        html, body, [class*="css"] {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .stApp {
            __APP_BACKGROUND__
        }

        __LOGIN_BACKGROUND__

        header[data-testid="stHeader"] {
            background: transparent;
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.2rem;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {
            color: var(--text-light) !important;
        }

        section[data-testid="stSidebar"] div.stButton > button {
            width: 100%;
            border-radius: 14px;
            padding: 0.75rem 0.9rem;
            margin: 0.12rem 0;
            background: transparent;
            border: 1px solid transparent;
            color: #dbeafe;
            text-align: left;
            justify-content: flex-start;
            font-weight: 700;
            transition: all 0.18s ease;
        }

        section[data-testid="stSidebar"] div.stButton > button:hover {
            background: rgba(37, 99, 235, 0.16);
            border: 1px solid rgba(147, 197, 253, 0.25);
            transform: translateX(2px);
        }

        section[data-testid="stSidebar"] div.stButton > button:focus {
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.35);
        }

        .brand-card {
            background: linear-gradient(135deg, rgba(37,99,235,0.95), rgba(124,58,237,0.95));
            border-radius: 22px;
            padding: 1.2rem;
            color: white;
            box-shadow: 0 20px 45px rgba(37, 99, 235, 0.28);
            margin-bottom: 1rem;
        }

        .brand-title {
            font-size: 1.35rem;
            font-weight: 900;
            letter-spacing: -0.03em;
            margin-bottom: 0.2rem;
        }

        .brand-subtitle {
            font-size: 0.78rem;
            color: rgba(255,255,255,0.78);
            line-height: 1.35;
        }

        .sidebar-section {
            margin-top: 1.2rem;
            margin-bottom: 0.45rem;
            color: #94a3b8;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 800;
        }

        .sidebar-active {
            background: rgba(37, 99, 235, 0.22);
            border: 1px solid rgba(147, 197, 253, 0.35);
            color: white;
            border-radius: 14px;
            padding: 0.72rem 0.9rem;
            font-weight: 900;
            margin: 0.18rem 0 0.32rem 0;
        }

        .profile-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 18px;
            padding: 1rem;
            margin-top: 1.4rem;
        }

        .profile-name {
            font-weight: 900;
            color: white;
            margin-bottom: 0.2rem;
        }

        .profile-role {
            color: #94a3b8;
            font-size: 0.78rem;
        }

        .hero-card {
            background:
                linear-gradient(135deg, rgba(255,255,255,0.92), rgba(248,250,252,0.88)),
                radial-gradient(circle at top right, rgba(37,99,235,0.13), transparent 28%);
            border: 1px solid rgba(226,232,240,0.9);
            border-radius: 28px;
            padding: 1.4rem 1.6rem;
            box-shadow: var(--shadow);
            margin-bottom: 1.25rem;
        }

        .hero-title {
            color: var(--text-main);
            font-size: clamp(1.5rem, 2vw, 2.25rem);
            font-weight: 950;
            letter-spacing: -0.055em;
            margin-bottom: 0.2rem;
        }

        .hero-subtitle {
            color: var(--text-muted);
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.42rem 0.72rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 850;
            border: 1px solid var(--border);
            background: white;
            color: var(--text-main);
            margin-right: 0.35rem;
            margin-top: 0.6rem;
        }

        .status-dot {
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 999px;
            background: var(--green);
            display: inline-block;
        }

        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            box-shadow: var(--shadow-soft);
            min-height: 130px;
            position: relative;
            overflow: hidden;
        }

        .metric-card::after {
            content: "";
            position: absolute;
            top: -36px;
            right: -36px;
            width: 96px;
            height: 96px;
            background: rgba(37,99,235,0.08);
            border-radius: 999px;
        }

        .metric-label {
            color: var(--text-muted);
            font-weight: 800;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.045em;
        }

        .metric-value {
            color: var(--text-main);
            font-size: 2rem;
            font-weight: 950;
            letter-spacing: -0.055em;
            margin-top: 0.35rem;
        }

        .metric-help {
            color: var(--text-muted);
            font-size: 0.82rem;
            margin-top: 0.25rem;
        }

        .glass-card {
            background: rgba(255,255,255,0.9);
            border: 1px solid rgba(226,232,240,0.9);
            border-radius: 24px;
            padding: 1.2rem;
            box-shadow: var(--shadow-soft);
            margin-bottom: 1.1rem;
        }

        .section-title {
            color: var(--text-main);
            font-size: 1.15rem;
            font-weight: 950;
            letter-spacing: -0.035em;
            margin-bottom: 0.25rem;
        }

        .section-subtitle {
            color: var(--text-muted);
            font-size: 0.88rem;
            margin-bottom: 1rem;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 900;
            border: 1px solid transparent;
        }

        .badge-low, .badge-pass, .badge-allow {
            background: var(--green-soft);
            color: #166534;
            border-color: #bbf7d0;
        }

        .badge-medium, .badge-warn {
            background: var(--yellow-soft);
            color: #92400e;
            border-color: #fde68a;
        }

        .badge-high, .badge-fail, .badge-block {
            background: var(--red-soft);
            color: #991b1b;
            border-color: #fecaca;
        }

        .insight-card {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: white;
            border-radius: 24px;
            padding: 1.25rem;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 1rem;
        }

        .insight-title {
            font-weight: 950;
            font-size: 1.05rem;
            margin-bottom: 0.35rem;
        }

        .insight-text {
            color: #cbd5e1;
            font-size: 0.88rem;
            line-height: 1.55;
        }

        .login-page-marker {
    display: none;
}

.stApp:has(.login-page-marker) .block-container {
    max-width: 100% !important;
    min-height: 100vh;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    display: flex;
    align-items: center;
    justify-content: center;
}

.stApp:has(.login-page-marker) .block-container > div {
    width: 100%;
}

.stApp:has(.login-page-marker) div[data-testid="stForm"] {
    max-width: 480px;
    margin: 0 auto;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,250,252,0.94));
    border: 1px solid rgba(226,232,240,0.95);
    border-radius: 30px;
    padding: 2rem;
    box-shadow: 0 30px 80px rgba(15, 23, 42, 0.13);
}

.login-logo {
    width: 54px;
    height: 54px;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    font-size: 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 16px 38px rgba(37, 99, 235, 0.34);
}

.login-title {
    color: var(--text-main);
    font-size: 1.75rem;
    font-weight: 950;
    letter-spacing: -0.055em;
    margin-bottom: 0.25rem;
}

.login-subtitle {
    color: var(--text-muted);
    font-size: 0.92rem;
    line-height: 1.5;
    margin-bottom: 1.3rem;
}

.login-demo-caption {
    max-width: 480px;
    margin: 0.75rem auto 0 auto;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.78rem;
}

        div.stTextInput > div > div > input,
        div.stNumberInput input,
        div.stTextArea textarea,
        div[data-baseweb="select"] > div {
            border-radius: 14px !important;
            border-color: #dbe3ef !important;
        }

        div.stTextInput > div > div > input:focus,
        div.stTextArea textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
        }

        div.stFormSubmitButton > button,
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
            border: none !important;
            border-radius: 14px !important;
            font-weight: 900 !important;
            box-shadow: 0 12px 30px rgba(37,99,235,0.24);
        }

        div.stFormSubmitButton > button:hover,
        div.stButton > button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 16px 36px rgba(37,99,235,0.30);
        }

        .empty-state {
            background: white;
            border: 1px dashed #cbd5e1;
            border-radius: 24px;
            padding: 2rem;
            text-align: center;
            color: var(--text-muted);
        }

        .empty-icon {
            font-size: 2.2rem;
            margin-bottom: 0.4rem;
        }

         .mini-label {
    color: var(--text-muted);
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    }

.risk-threshold-list {
    margin-top: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
}

.risk-threshold-row {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    color: #cbd5e1;
    font-size: 0.78rem;
    font-weight: 750;
}

.risk-dot {
    width: 9px;
    height: 9px;
    border-radius: 999px;
    display: inline-block;
    flex-shrink: 0;
    box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.04);
}

.risk-dot-low {
    background: #22c55e;
}

.risk-dot-medium {
    background: #f59e0b;
}

.risk-dot-high {
    background: #ef4444;
}

.risk-threshold-text {
    color: #e5e7eb;
    font-weight: 850;
    margin-right: 0.25rem;
}

.risk-threshold-range {
    color: #94a3b8;
    font-weight: 650;
}

        .result-panel {
            background:
                linear-gradient(135deg, #ffffff, #f8fafc);
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 1.3rem;
            box-shadow: var(--shadow);
        }

        .result-main {
            font-size: 2rem;
            font-weight: 950;
            letter-spacing: -0.05em;
        }

        .footer-note {
            color: #94a3b8;
            font-size: 0.72rem;
            margin-top: 0.9rem;
            line-height: 1.45;
        }

        @media (max-width: 1100px) {
            .metric-card {
                min-height: 116px;
            }

            .metric-value {
                font-size: 1.55rem;
            }

            .hero-card {
                padding: 1.1rem;
            }
        }

        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .hero-title {
                font-size: 1.45rem;
            }

            .login-card {
                margin-top: 1rem;
                padding: 1.4rem;
            }
        }
         </style>
        """

    app_background_css = """
    background: #f8fafc !important;
"""

    app_background_css = """
        background: #f8fafc !important;
    """

    if bg_image_base64:
        login_background_css = f"""
        .stApp:has(.login-page-marker) {{
            background:
                linear-gradient(rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.03)),
                url("data:image/jpeg;base64,{bg_image_base64}") !important;
            background-size: cover !important;
            background-position: center center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        """
    else:
        login_background_css = ""

    css = css.replace("__APP_BACKGROUND__", app_background_css)
    css = css.replace("__LOGIN_BACKGROUND__", login_background_css)

    st.markdown(css, unsafe_allow_html=True)


# ============================================================
# DATA HELPERS
# ============================================================

def load_history():
    """
    Load prediction history from the same CSV used by the FastAPI backend.

    app.py is inside:
        deploypilot-ai/dashboard/pages/app.py

    FastAPI saves prediction history here:
        deploypilot-ai/data/prediction_history.csv

    Therefore this function reads:
        PROJECT_ROOT / "data" / "prediction_history.csv"

    It does not fall back to demo/sample data, because that hides real path errors.
    """
    if not HISTORY_FILE.exists():
        st.error(f"Prediction history CSV not found: {HISTORY_FILE}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(HISTORY_FILE)

        if df.empty:
            st.warning(f"Prediction history CSV is empty: {HISTORY_FILE}")
            return pd.DataFrame()

        df = prepare_history_dataframe(df)

        if "timestamp" in df.columns:
            df = df.sort_values("timestamp", ascending=True, na_position="last")

        return df

    except Exception as error:
        st.error(f"Could not read prediction history CSV: {HISTORY_FILE}")
        st.exception(error)
        return pd.DataFrame()


def prepare_history_dataframe(df):
    df = df.copy()

    # Remove accidental spaces from column names
    df.columns = df.columns.astype(str).str.strip()

    # Convert timestamp strings to datetime values
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    numeric_columns = [
        "commit_size",
        "files_changed",
        "warnings",
        "tests_failed",
        "build_duration_sec",
        "test_duration_sec",
        "deploy_duration_sec",
        "previous_failure_rate",
        "risk_score",
        "retry_count"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    text_columns = [
        "pipeline_id",
        "run_id",
        "ci_tool",
        "repository",
        "branch",
        "prediction",
        "risk_level",
        "failure_type",
        "recommendation",
        "preventive_advice",
        "quality_gate_action",
        "threshold_explanation",
        "actual_result"
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].fillna("").astype(str).str.strip()

    # Normalize values so counts, filters, and badges work correctly
    if "prediction" in df.columns:
        df["prediction"] = df["prediction"].str.upper()

    if "risk_level" in df.columns:
        df["risk_level"] = df["risk_level"].str.upper()

    if "quality_gate_action" in df.columns:
        df["quality_gate_action"] = df["quality_gate_action"].str.upper()

    if "actual_result" in df.columns:
        df["actual_result"] = df["actual_result"].str.upper()

    if "failure_type" in df.columns:
        df["failure_type"] = df["failure_type"].replace("", "None")

    return df


def create_sample_history():
    now = pd.Timestamp.now()

    rows = [
        {
            "timestamp": now - pd.Timedelta(hours=10),
            "pipeline_id": "sample_001",
            "run_id": "run_001",
            "ci_tool": "GitHub Actions",
            "repository": "deploypilot-demo",
            "branch": "dev",
            "commit_size": 8,
            "files_changed": 2,
            "warnings": 0,
            "tests_failed": 0,
            "build_duration_sec": 72,
            "test_duration_sec": 36,
            "deploy_duration_sec": 15,
            "previous_failure_rate": 0.05,
            "prediction": "PASS",
            "risk_score": 0.14,
            "risk_level": "LOW",
            "failure_type": "None",
            "quality_gate_action": "ALLOW",
            "actual_result": "PASS"
        },
        {
            "timestamp": now - pd.Timedelta(hours=8),
            "pipeline_id": "sample_002",
            "run_id": "run_002",
            "ci_tool": "GitHub Actions",
            "repository": "deploypilot-demo",
            "branch": "main",
            "commit_size": 44,
            "files_changed": 11,
            "warnings": 5,
            "tests_failed": 3,
            "build_duration_sec": 384,
            "test_duration_sec": 221,
            "deploy_duration_sec": 0,
            "previous_failure_rate": 0.41,
            "prediction": "FAIL",
            "risk_score": 0.77,
            "risk_level": "HIGH",
            "failure_type": "Test Failure",
            "quality_gate_action": "BLOCK",
            "actual_result": "FAIL"
        },
        {
            "timestamp": now - pd.Timedelta(hours=6),
            "pipeline_id": "sample_003",
            "run_id": "run_003",
            "ci_tool": "GitHub Actions",
            "repository": "deploypilot-api",
            "branch": "qa",
            "commit_size": 21,
            "files_changed": 6,
            "warnings": 7,
            "tests_failed": 0,
            "build_duration_sec": 245,
            "test_duration_sec": 120,
            "deploy_duration_sec": 70,
            "previous_failure_rate": 0.25,
            "prediction": "FAIL",
            "risk_score": 0.52,
            "risk_level": "MEDIUM",
            "failure_type": "Dependency Error",
            "quality_gate_action": "WARN",
            "actual_result": "FAIL"
        },
        {
            "timestamp": now - pd.Timedelta(hours=4),
            "pipeline_id": "sample_004",
            "run_id": "run_004",
            "ci_tool": "Jenkins",
            "repository": "wallet-service",
            "branch": "release",
            "commit_size": 63,
            "files_changed": 18,
            "warnings": 8,
            "tests_failed": 0,
            "build_duration_sec": 520,
            "test_duration_sec": 180,
            "deploy_duration_sec": 210,
            "previous_failure_rate": 0.36,
            "prediction": "FAIL",
            "risk_score": 0.71,
            "risk_level": "HIGH",
            "failure_type": "Deployment Failure",
            "quality_gate_action": "BLOCK",
            "actual_result": "FAIL"
        },
        {
            "timestamp": now - pd.Timedelta(hours=1),
            "pipeline_id": "sample_005",
            "run_id": "run_005",
            "ci_tool": "GitLab CI",
            "repository": "payment-ui",
            "branch": "feature",
            "commit_size": 12,
            "files_changed": 3,
            "warnings": 2,
            "tests_failed": 0,
            "build_duration_sec": 110,
            "test_duration_sec": 54,
            "deploy_duration_sec": 20,
            "previous_failure_rate": 0.08,
            "prediction": "PASS",
            "risk_score": 0.22,
            "risk_level": "LOW",
            "failure_type": "None",
            "quality_gate_action": "ALLOW",
            "actual_result": "PASS"
        }
    ]

    return pd.DataFrame(rows)


def read_text_file(path):
    if path.exists():
        return path.read_text(encoding="utf-8")

    return "Metrics file has not been created yet. This will appear after ML model training."


def check_api_status():
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        model_response = requests.get(f"{API_BASE_URL}/model-status", timeout=2)

        if health_response.status_code == 200:
            model_status = {}
            if model_response.status_code == 200:
                model_status = model_response.json()

            return True, model_status

    except requests.exceptions.RequestException:
        pass

    return False, {}


def badge_html(value):
    value_text = str(value)

    css_class = "badge"

    lowered = value_text.lower()

    if lowered in ["low", "pass", "allow", "none"]:
        css_class += " badge-low"

    elif lowered in ["medium", "warn"]:
        css_class += " badge-medium"

    elif lowered in ["high", "fail", "block"]:
        css_class += " badge-high"

    return f'<span class="{css_class}">{value_text}</span>'


def metric_card(label, value, help_text, accent="blue"):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_header(title, subtitle):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# LOGIN PAGE
# ============================================================

# def login_page():
#     st.markdown(
#         """
#         <div class="login-card">
#             <div class="login-logo">🚀</div>
#             <div class="login-title">DeployPilot AI</div>
#             <div class="login-subtitle">
#                 Sign in to monitor CI/CD risk, quality gates, predictions, and DevOps intelligence.
#             </div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     left, center, right = st.columns([1, 1.15, 1])

#     with center:
#         with st.form("login_form"):
#             st.markdown("#### Secure Workspace Login")

#             email = st.text_input(
#                 "Email address",
#                 placeholder="admin@deploypilot.ai"
#             )

#             password = st.text_input(
#                 "Password",
#                 placeholder="Enter password",
#                 type="password"
#             )

#             remember = st.checkbox("Remember this device", value=True)

#             submitted = st.form_submit_button("Sign in to Dashboard", use_container_width=True)

#             if submitted:
#                 if not email or not password:
#                     st.error("Please enter both email and password.")

#                 elif email == "admin@deploypilot.ai" and password == "deploypilot123":
#                     st.session_state.authenticated = True
#                     st.session_state.user_name = "Manuja Sureshchandra"
#                     st.success("Login successful.")
#                     st.rerun()

#                 else:
#                     st.error("Invalid demo credentials.")

#         st.caption("Demo credentials: admin@deploypilot.ai / deploypilot123")

#-------------------------------------------------------------------------------------------------
# def login_page():
#     left, center, right = st.columns([1, 1.15, 1])

#     with center:
#         with st.form("login_form"):
#             st.markdown(
#                 """
#                 <div style="text-align:left; margin-bottom:1.4rem;">
#                     <div class="login-logo">🚀</div>
#                     <div class="login-title">DeployPilot AI</div>
#                     <div class="login-subtitle">
#                         Sign in to monitor CI/CD risk, quality gates, predictions, and DevOps intelligence.
#                     </div>
#                 </div>
#                 """,
#                 unsafe_allow_html=True
#             )

#             email = st.text_input(
#                 "Email address",
#                 placeholder="admin@deploypilot.ai"
#             )

#             password = st.text_input(
#                 "Password",
#                 placeholder="Enter password",
#                 type="password"
#             )

#             remember = st.checkbox("Remember this device", value=True)

#             submitted = st.form_submit_button("Sign in to Dashboard", use_container_width=True)

#             if submitted:
#                 if not email or not password:
#                     st.error("Please enter both email and password.")

#                 elif email == "admin@deploypilot.ai" and password == "deploypilot123":
#                     st.session_state.authenticated = True
#                     st.session_state.user_name = "Manuja Sureshchandra"
#                     st.success("Login successful.")
#                     st.rerun()

#                 else:
#                     st.error("Invalid demo credentials.")

#         st.caption("Demo credentials: admin@deploypilot.ai / deploypilot123")
# -------------------------------------------------------------------------------------------------
def login_page():
    st.markdown('<div class="login-page-marker"></div>', unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown(
            """
            <div>
                <div class="login-logo">🚀</div>
                <div class="login-title">DeployPilot AI</div>
                <div class="login-subtitle">
                    Sign in to monitor CI/CD risk, quality gates and predictions
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        email = st.text_input(
            "Email address",
            placeholder="admin@deploypilot.ai"
        )

        password = st.text_input(
            "Password",
            placeholder="Enter password",
            type="password"
        )

        remember = st.checkbox("Remember this device", value=True)

        submitted = st.form_submit_button("Sign in to Dashboard", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")

            elif email == "admin@deploypilot.ai" and password == "deploypilot123":
                st.session_state.authenticated = True
                st.session_state.user_name = "Manuja Chamuditha"
                st.success("Login successful.")
                st.rerun()

            else:
                st.error("Invalid demo credentials.")

    st.markdown(
        """
        <div class="login-demo-caption">
            Demo credentials: admin@deploypilot.ai / deploypilot123
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def sidebar_navigation():
    st.sidebar.markdown(
        """
        <div class="brand-card">
            <div class="brand-title">DeployPilot AI</div>
            <div class="brand-subtitle">
                Intelligent CI/CD failure prediction and risk control platform.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)

    nav_items = [
      ("Dashboard Overview", ""),
      ("Manual Prediction", ""),
      ("Pipeline History", ""),
      ("Analytics", ""),
      ("Model Evaluation", ""),

    ]

    for page_name, icon in nav_items:
        if st.session_state.current_page == page_name:
            st.sidebar.markdown(
                f'<div class="sidebar-active">{icon} {page_name}</div>',
                unsafe_allow_html=True
            )
        else:
            if st.sidebar.button(
                f"{icon} {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True
            ):
                st.session_state.current_page = page_name
                st.rerun()

    st.sidebar.markdown('<div class="sidebar-section">Risk Thresholds</div>', unsafe_allow_html=True)

    st.sidebar.markdown(
    """
    <div class="profile-card">
        <div class="mini-label">Quality Gate</div>
        <div class="risk-threshold-list">
            <div class="risk-threshold-row"><span class="risk-dot risk-dot-low"></span><span class="risk-threshold-text">LOW</span><span class="risk-threshold-range">0.00–0.39</span></div>
            <div class="risk-threshold-row"><span class="risk-dot risk-dot-medium"></span><span class="risk-threshold-text">MEDIUM</span><span class="risk-threshold-range">0.40–0.69</span></div>
            <div class="risk-threshold-row"><span class="risk-dot risk-dot-high"></span><span class="risk-threshold-text">HIGH</span><span class="risk-threshold-range">0.70–1.00</span></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

    st.sidebar.markdown(
        f"""
        <div class="profile-card">
            <div class="profile-name">👤 {st.session_state.user_name}</div>
            <div class="profile-role">Devops Engineer</div>
            <div class="footer-note">
                MVP mode: FastAPI + CSV storage. ML models will be connected after training.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_page = "Dashboard Overview"
        st.rerun()


# ============================================================
# HEADER
# ============================================================

def page_hero():
    api_online, model_status = check_api_status()

    api_text = "API Online" if api_online else "API Offline"
    model_1_text = "Model 1 Loaded" if model_status.get("failure_risk_model_loaded") else "Fallback Risk Logic"
    model_2_text = "Model 2 Loaded" if model_status.get("failure_type_classifier_loaded") else "Fallback Log Classifier"

    dot_color = "#16a34a" if api_online else "#dc2626"

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">DeployPilot AI Command Center</div>
            <div class="hero-subtitle">
                Enterprise-style DevOps intelligence dashboard for CI/CD failure prediction,
                quality gate decisions, risk trends, recommendations, and model evaluation.
            </div>
            <div>
                <span class="status-pill">
                    <span class="status-dot" style="background:{dot_color};"></span>
                    {api_text}
                </span>
                <span class="status-pill">🧠 {model_1_text}</span>
                <span class="status-pill">🧾 {model_2_text}</span>
                <span class="status-pill">💾 CSV Storage</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD OVERVIEW PAGE
# ============================================================

def dashboard_overview_page():
    page_hero()

    history_df = load_history()

    if history_df.empty:
        st.info("No prediction history records found. Check the CSV path or run a prediction first.")
        return

    total_predictions = len(history_df)

    pass_count = int((history_df["prediction"] == "PASS").sum()) if "prediction" in history_df else 0
    fail_count = int((history_df["prediction"] == "FAIL").sum()) if "prediction" in history_df else 0

    fail_rate = (fail_count / total_predictions * 100) if total_predictions > 0 else 0

    average_risk = history_df["risk_score"].mean() if "risk_score" in history_df else 0

    blocked_count = int((history_df["quality_gate_action"] == "BLOCK").sum()) if "quality_gate_action" in history_df else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Total Runs", f"{total_predictions:,}", "Prediction records tracked")

    with col2:
        metric_card("Fail Rate", f"{fail_rate:.1f}%", "Predicted failure ratio")

    with col3:
        metric_card("Average Risk", f"{average_risk:.2f}", "Mean failure probability")

    with col4:
        metric_card("Blocked Runs", f"{blocked_count:,}", "Quality gate BLOCK actions")

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1.2, 0.8])

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header(
            "Risk Trend",
            "Shows how predicted pipeline risk changes across recent runs."
        )

        risk_df = history_df.copy()
        risk_df["record_number"] = range(1, len(risk_df) + 1)

        fig = px.line(
            risk_df,
            x="record_number",
            y="risk_score",
            markers=True,
            title=None
        )

        fig.add_hrect(
            y0=0.70,
            y1=1.0,
            fillcolor="rgba(220,38,38,0.08)",
            line_width=0
        )

        fig.add_hrect(
            y0=0.40,
            y1=0.69,
            fillcolor="rgba(217,119,6,0.08)",
            line_width=0
        )

        fig.update_layout(
            height=355,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis_title="Risk Score",
            xaxis_title="Run Number"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-title">AI Insight Summary</div>
                <div class="insight-text">
                    High-risk builds are blocked when the quality gate is enabled.
                    Medium-risk builds continue with warnings. Low-risk builds are allowed
                    to continue normally. This supports early risk control before deployment.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("System Health", "Live backend and storage status.")

        api_online, model_status = check_api_status()

        st.markdown(f"API Status: {badge_html('Online' if api_online else 'Offline')}", unsafe_allow_html=True)
        st.markdown(f"Risk Model: {badge_html('Loaded' if model_status.get('failure_risk_model_loaded') else 'Fallback')}", unsafe_allow_html=True)
        st.markdown(f"Type Classifier: {badge_html('Loaded' if model_status.get('failure_type_classifier_loaded') else 'Fallback')}", unsafe_allow_html=True)
        st.markdown(f"Storage: {badge_html('CSV')}", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_header("Recent Pipeline Activity", "Latest predictions saved into prediction_history.csv.")

    recent_columns = [
        "timestamp",
        "pipeline_id",
        "repository",
        "branch",
        "prediction",
        "risk_score",
        "risk_level",
        "failure_type",
        "quality_gate_action"
    ]

    visible_columns = [column for column in recent_columns if column in history_df.columns]

    recent_df = history_df.sort_values("timestamp", ascending=False) if "timestamp" in history_df.columns else history_df

    st.dataframe(
        recent_df[visible_columns].head(8),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MANUAL PREDICTION PAGE
# ============================================================

def manual_prediction_page():
    page_hero()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_header(
        "Manual Pipeline Prediction",
        "Send CI/CD metadata and log data to the FastAPI prediction service."
    )

    with st.form("manual_prediction_form"):
        top1, top2, top3 = st.columns(3)

        with top1:
            pipeline_id = st.text_input("Pipeline ID", "streamlit_pipeline_001")
            run_id = st.text_input("Run ID", "streamlit_run_001")
            repository = st.text_input("Repository", "deploypilot-demo")
            branch = st.selectbox("Branch", ["dev", "qa", "main", "feature", "release"], index=2)

        with top2:
            ci_tool = st.selectbox("CI Tool", ["GitHub Actions", "Jenkins", "GitLab CI", "Azure DevOps"])
            language = st.selectbox("Language", ["Python", "JavaScript", "Java", "C#", "Go", "Other"])
            os_name = st.selectbox("OS", ["ubuntu-latest", "windows-latest", "macos-latest"])
            cloud_provider = st.selectbox("Cloud Provider", ["GitHub Hosted", "AWS", "Azure", "GCP", "Self-Hosted", "Unknown"])

        with top3:
            quality_gate_enabled = st.toggle("Enable Quality Gate", value=True)
            actual_result = st.selectbox("Actual Result", ["", "PASS", "FAIL"])
            st.info("Use high-risk defaults for demo BLOCK output.")

        st.divider()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            commit_size = st.number_input("Commit Size", min_value=0, value=40)
            files_changed = st.number_input("Files Changed", min_value=0, value=12)

        with col2:
            warnings = st.number_input("Warnings", min_value=0, value=5)
            tests_failed = st.number_input("Tests Failed", min_value=0, value=3)

        with col3:
            build_duration_sec = st.number_input("Build Duration Seconds", min_value=0.0, value=400.0)
            test_duration_sec = st.number_input("Test Duration Seconds", min_value=0.0, value=240.0)

        with col4:
            deploy_duration_sec = st.number_input("Deploy Duration Seconds", min_value=0.0, value=0.0)
            retry_count = st.number_input("Retry Count", min_value=0, value=1)

        col5, col6, col7 = st.columns(3)

        with col5:
            previous_failure_rate = st.slider("Previous Failure Rate", 0.0, 1.0, 0.4, 0.01)

        with col6:
            cpu_usage_pct = st.slider("CPU Usage %", 0.0, 100.0, 75.5, 0.5)

        with col7:
            memory_usage_mb = st.number_input("Memory Usage MB", min_value=0.0, value=3200.0)

        error_log = st.text_area(
            "CI/CD Error Log",
            value="2026-07-01 10:44:21 /home/runner/project/test_login.py AssertionError expected 200 got 500",
            height=150
        )

        submitted = st.form_submit_button("Run AI Prediction", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        payload = {
            "pipeline_id": pipeline_id,
            "run_id": run_id,
            "ci_tool": ci_tool,
            "repository": repository,
            "branch": branch,
            "commit_size": commit_size,
            "files_changed": files_changed,
            "warnings": warnings,
            "tests_failed": tests_failed,
            "build_duration_sec": build_duration_sec,
            "test_duration_sec": test_duration_sec,
            "deploy_duration_sec": deploy_duration_sec,
            "cpu_usage_pct": cpu_usage_pct,
            "memory_usage_mb": memory_usage_mb,
            "retry_count": retry_count,
            "previous_failure_rate": previous_failure_rate,
            "language": language,
            "os": os_name,
            "cloud_provider": cloud_provider,
            "error_log": error_log,
            "quality_gate_enabled": quality_gate_enabled,
            "actual_result": actual_result
        }

        try:
            response = requests.post(PREDICT_URL, json=payload, timeout=12)

            if response.status_code == 200:
                result = response.json()

                st.markdown('<div class="result-panel">', unsafe_allow_html=True)
                section_header(
                    "Prediction Result Panel",
                    "AI prediction, risk level, failure category, recommendation, and gate decision."
                )

                r1, r2, r3, r4 = st.columns(4)

                with r1:
                    metric_card("Prediction", result["prediction"], "PASS or FAIL output")

                with r2:
                    metric_card("Risk Score", f'{result["risk_score"]:.4f}', "Probability of failure")

                with r3:
                    metric_card("Risk Level", result["risk_level"], "LOW / MEDIUM / HIGH")

                with r4:
                    metric_card("Gate Action", result["quality_gate_action"], "ALLOW / WARN / BLOCK")

                st.markdown("### Failure Type")
                st.markdown(badge_html(result["failure_type"]), unsafe_allow_html=True)

                st.markdown("### Recommendation")
                st.write(result["recommendation"])

                st.markdown("### Preventive Advice")
                st.write(result["preventive_advice"])

                st.markdown("### Threshold Explanation")
                st.info(result["threshold_explanation"])

                st.markdown("### Cleaned Log Preview")
                st.code(result["cleaned_log_preview"] or "No log content available.", language="text")

                with st.expander("View Full JSON Response"):
                    st.json(result)

                st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.error(f"FastAPI returned status code {response.status_code}")
                st.code(response.text)

        except requests.exceptions.ConnectionError:
            st.error("FastAPI is not running. Start it using: uvicorn api.main:app --reload")

        except requests.exceptions.Timeout:
            st.error("FastAPI request timed out.")


# ============================================================
# PIPELINE HISTORY PAGE
# ============================================================

def pipeline_history_page():
    page_hero()

    history_df = load_history()

    if history_df.empty:
        st.info("No prediction history records found. Check the CSV path or run a prediction first.")
        return

    if "timestamp" in history_df.columns:
        history_df = history_df.sort_values("timestamp", ascending=False, na_position="last")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_header(
        "Pipeline History",
        "Search, filter, and review stored CI/CD prediction records."
    )

    search = st.text_input(
        "Search pipeline ID, run ID, repository, branch, failure type, or action",
        placeholder="Search history..."
    )

    filtered_df = history_df.copy()

    if search:
        search_lower = search.lower()
        filtered_df = filtered_df[
            filtered_df.astype(str).apply(
                lambda row: row.str.lower().str.contains(search_lower).any(),
                axis=1
            )
        ]

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        if "prediction" in filtered_df.columns:
            selected_predictions = st.multiselect(
                "Prediction",
                sorted(filtered_df["prediction"].dropna().unique())
            )

            if selected_predictions:
                filtered_df = filtered_df[filtered_df["prediction"].isin(selected_predictions)]

    with f2:
        if "risk_level" in filtered_df.columns:
            selected_risk = st.multiselect(
                "Risk Level",
                sorted(filtered_df["risk_level"].dropna().unique())
            )

            if selected_risk:
                filtered_df = filtered_df[filtered_df["risk_level"].isin(selected_risk)]

    with f3:
        if "quality_gate_action" in filtered_df.columns:
            selected_actions = st.multiselect(
                "Gate Action",
                sorted(filtered_df["quality_gate_action"].dropna().unique())
            )

            if selected_actions:
                filtered_df = filtered_df[filtered_df["quality_gate_action"].isin(selected_actions)]

    with f4:
        if "failure_type" in filtered_df.columns:
            selected_failure = st.multiselect(
                "Failure Type",
                sorted(filtered_df["failure_type"].dropna().unique())
            )

            if selected_failure:
                filtered_df = filtered_df[filtered_df["failure_type"].isin(selected_failure)]

    st.caption(f"Showing {len(filtered_df)} record(s).")

    display_columns = [
        "timestamp",
        "pipeline_id",
        "run_id",
        "ci_tool",
        "repository",
        "branch",
        "prediction",
        "risk_score",
        "risk_level",
        "failure_type",
        "quality_gate_action",
        "actual_result"
    ]

    visible_columns = [column for column in display_columns if column in filtered_df.columns]

    st.dataframe(
        filtered_df[visible_columns],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# ANALYTICS PAGE
# ============================================================

def analytics_page():
    page_hero()

    history_df = load_history()

    if history_df.empty:
        st.info("No prediction history records found. Check the CSV path or run a prediction first.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("PASS vs FAIL", "Distribution of prediction outcomes.")

        if "prediction" in history_df.columns:
            counts = history_df["prediction"].value_counts().reset_index()
            counts.columns = ["prediction", "count"]

            fig = px.bar(
                counts,
                x="prediction",
                y="count",
                text="count",
                color="prediction",
                color_discrete_map={
                    "PASS": "#16a34a",
                    "FAIL": "#dc2626"
                }
            )

            fig.update_layout(
                height=330,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Quality Gate Actions", "ALLOW, WARN, and BLOCK decisions.")

        if "quality_gate_action" in history_df.columns:
            counts = history_df["quality_gate_action"].value_counts().reset_index()
            counts.columns = ["quality_gate_action", "count"]

            fig = px.pie(
                counts,
                names="quality_gate_action",
                values="count",
                hole=0.55
            )

            fig.update_layout(
                height=330,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Failure Type Distribution", "Most common predicted CI/CD failure categories.")

        if "failure_type" in history_df.columns:
            failure_df = history_df[history_df["failure_type"].astype(str) != "None"]
            counts = failure_df["failure_type"].value_counts().reset_index()
            counts.columns = ["failure_type", "count"]

            fig = px.bar(
                counts,
                x="count",
                y="failure_type",
                orientation="h",
                text="count"
            )

            fig.update_layout(
                height=360,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis_title=None
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Build Duration by Prediction", "Compare build duration between PASS and FAIL predictions.")

        if "build_duration_sec" in history_df.columns and "prediction" in history_df.columns:
            fig = px.box(
                history_df,
                x="prediction",
                y="build_duration_sec",
                color="prediction",
                color_discrete_map={
                    "PASS": "#16a34a",
                    "FAIL": "#dc2626"
                }
            )

            fig.update_layout(
                height=360,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_header("Risk Score Over Time", "Timeline of CI/CD risk predictions.")

    timeline_df = history_df.copy()
    timeline_df["record_number"] = range(1, len(timeline_df) + 1)

    fig = px.area(
        timeline_df,
        x="record_number",
        y="risk_score",
        markers=True
    )

    fig.add_hline(y=0.40, line_dash="dash", line_color="#d97706")
    fig.add_hline(y=0.70, line_dash="dash", line_color="#dc2626")

    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Risk Score",
        xaxis_title="Run Number"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MODEL EVALUATION PAGE
# ============================================================

def model_evaluation_page():
    page_hero()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_header(
        "Model Evaluation",
        "Accuracy, precision, recall, F1-score, ROC-AUC, and confusion matrix evidence."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Accuracy", "Pending", "Available after Model 1 training")

    with c2:
        metric_card("Precision", "Pending", "Available after Model 1 training")

    with c3:
        metric_card("Recall", "Pending", "Available after Model 1 training")

    with c4:
        metric_card("F1 Score", "Pending", "Quality gate reliability metric")

    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Model 1 — Failure Risk Prediction", "RandomForestClassifier metrics.")

        st.text(read_text_file(MODEL_1_METRICS_FILE))

        if MODEL_1_CONFUSION_MATRIX.exists():
            st.image(str(MODEL_1_CONFUSION_MATRIX), caption="Model 1 Confusion Matrix")
        else:
            st.info("Model 1 confusion matrix will appear after training.")

        if MODEL_1_ROC_CURVE.exists():
            st.image(str(MODEL_1_ROC_CURVE), caption="Model 1 ROC Curve")
        else:
            st.info("Model 1 ROC curve will appear after training.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Model 2 — Failure Type Classifier", "TF-IDF + Logistic Regression metrics.")

        st.text(read_text_file(MODEL_2_METRICS_FILE))

        if MODEL_2_CONFUSION_MATRIX.exists():
            st.image(str(MODEL_2_CONFUSION_MATRIX), caption="Model 2 Confusion Matrix")
        else:
            st.info("Model 2 confusion matrix will appear after training.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_header("Metric Explanation for Viva", "Simple explanations for academic presentation.")

    st.markdown(
        """
        **Accuracy** shows the overall percentage of correct predictions.

        **Precision** shows how many predicted failures were actually failures. This helps reduce unnecessary blocking.

        **Recall** shows how many real failures were successfully detected. This helps prevent risky builds from passing.

        **F1-score** balances precision and recall. It is important for the quality gate because the system must detect risky builds without continuously blocking safe builds.

        **ROC-AUC** shows how well the model separates high-risk builds from low-risk builds across different threshold values.
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MAIN APP
# ============================================================

def main():
    inject_css()

    if not st.session_state.authenticated:
        login_page()
        return

    sidebar_navigation()

    page = st.session_state.current_page

    if page == "Dashboard Overview":
        dashboard_overview_page()

    elif page == "Manual Prediction":
        manual_prediction_page()

    elif page == "Pipeline History":
        pipeline_history_page()

    elif page == "Analytics":
        analytics_page()

    elif page == "Model Evaluation":
        model_evaluation_page()


if __name__ == "__main__":
    main()