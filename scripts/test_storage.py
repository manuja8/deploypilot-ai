from api.storage import (
    initialize_history_file,
    save_prediction,
    load_prediction_history
)


print("Initializing prediction history file...")

history_file = initialize_history_file()

print("History file path:")
print(history_file)


sample_prediction = {
    "pipeline_id": "pipeline_001",
    "run_id": "github_run_001",
    "ci_tool": "GitHub Actions",
    "repository": "deploypilot-demo",
    "branch": "dev",
    "commit_size": 45,
    "files_changed": 8,
    "warnings": 6,
    "tests_failed": 2,
    "build_duration_sec": 320,
    "test_duration_sec": 180,
    "deploy_duration_sec": 0,
    "previous_failure_rate": 0.35,
    "prediction": "FAIL",
    "risk_score": 0.82,
    "risk_level": "HIGH",
    "failure_type": "Test Failure",
    "recommendation": "Review failed test cases and run tests locally before pushing again.",
    "preventive_advice": "Run unit tests locally before pushing similar changes.",
    "quality_gate_action": "BLOCK",
    "threshold_explanation": "Risk score is between 0.70 and 1.00. The pipeline is considered high risk, so the quality gate blocks the run.",
    "actual_result": "FAIL"
}


print("\nSaving sample prediction...")

saved_row = save_prediction(sample_prediction)

print("Saved row:")
print(saved_row)


print("\nLoading prediction history...")

history_df = load_prediction_history()

print(history_df.tail())

#python -m scripts.test_storage.py