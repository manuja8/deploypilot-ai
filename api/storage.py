from pathlib import Path
from datetime import datetime

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

HISTORY_FILE = (
    PROJECT_ROOT
    / "data"
    / "prediction_history.csv"
)


HISTORY_COLUMNS = [
    "timestamp",
    "pipeline_id",
    "run_id",
    "ci_tool",
    "repository",
    "branch",
    "commit_size",
    "files_changed",
    "warnings",
    "tests_failed",
    "build_duration_sec",
    "test_duration_sec",
    "deploy_duration_sec",
    "previous_failure_rate",
    "prediction",
    "risk_score",
    "risk_level",
    "failure_type",
    "recommendation",
    "preventive_advice",
    "quality_gate_action",
    "threshold_explanation",
    "actual_result"
]


def initialize_history_file():
    """
    Create prediction_history.csv if it does not exist
    or if it exists but is empty.
    """

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    file_missing = not HISTORY_FILE.exists()
    file_empty = HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size == 0

    if file_missing or file_empty:
        empty_df = pd.DataFrame(
            columns=HISTORY_COLUMNS
        )

        empty_df.to_csv(
            HISTORY_FILE,
            index=False
        )

    return HISTORY_FILE


def save_prediction(result_dict):
    """
    Save one prediction result into prediction_history.csv.

    Missing values are stored as empty strings so the CSV remains stable.
    """

    initialize_history_file()

    row = {}

    for column in HISTORY_COLUMNS:
        row[column] = result_dict.get(column, "")

    if not row["timestamp"]:
        row["timestamp"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    try:
        existing_df = pd.read_csv(HISTORY_FILE)
    except pd.errors.EmptyDataError:
        existing_df = pd.DataFrame(columns=HISTORY_COLUMNS)

    new_row_df = pd.DataFrame([row])

    updated_df = pd.concat(
        [existing_df, new_row_df],
        ignore_index=True
    )

    updated_df.to_csv(
        HISTORY_FILE,
        index=False
    )

    return row


def load_prediction_history():
    """
    Load prediction history from prediction_history.csv.
    """

    initialize_history_file()

    history_df = pd.read_csv(HISTORY_FILE)

    return history_df