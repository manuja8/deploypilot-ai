import pandas as pd

from api.log_preprocessor import clean_log
from api.model_loader import load_models
from api.quality_gate import evaluate_quality_gate
from api.recommendation_engine import generate_recommendation
from api.history_repository import HistoryRepository


MODEL_1_FEATURES = [
    "commit_size",
    "files_changed",
    "warnings",
    "tests_failed",
    "previous_failure_rate",
    "build_duration_sec",
    "test_duration_sec",
    "deploy_duration_sec",
    "cpu_usage_pct",
    "memory_usage_mb",
    "retry_count",
    "ci_tool",
    "branch",
    "language",
    "os",
    "cloud_provider"
]


loaded_models = load_models()

failure_risk_model = loaded_models["failure_risk_model"]
failure_type_classifier = loaded_models["failure_type_classifier"]


def predict_pipeline_risk(request_data):
    """
    Predict CI/CD pipeline risk.

    If the trained Failure Risk Model exists, use the .pkl model.
    If it does not exist yet, use temporary fallback logic.
    """

    input_dict = request_data.dict()

    if failure_risk_model is not None:
        input_df = pd.DataFrame(
            [
                {
                    feature: input_dict.get(feature)
                    for feature in MODEL_1_FEATURES
                }
            ]
        )

        input_df["cloud_provider"] = (
            input_df["cloud_provider"]
            .fillna("Unknown")
        )

        prediction = failure_risk_model.predict(input_df)[0]

        probabilities = failure_risk_model.predict_proba(input_df)[0]
        model_classes = list(failure_risk_model.classes_)

        fail_index = model_classes.index("FAIL")
        risk_score = float(probabilities[fail_index])

        return prediction, round(risk_score, 4)

    risk_score = calculate_fallback_risk_score(input_dict)

    if risk_score >= 0.50:
        prediction = "FAIL"
    else:
        prediction = "PASS"

    return prediction, round(risk_score, 4)


def calculate_fallback_risk_score(input_dict):
    """
    Temporary fallback risk scoring until Model 1 is trained.

    This is not the final ML model.
    It only helps the FastAPI MVP work before the .pkl model exists.
    """

    tests_failed = float(input_dict.get("tests_failed", 0))
    warnings = float(input_dict.get("warnings", 0))
    previous_failure_rate = float(input_dict.get("previous_failure_rate", 0))
    retry_count = float(input_dict.get("retry_count", 0))
    commit_size = float(input_dict.get("commit_size", 0))
    files_changed = float(input_dict.get("files_changed", 0))
    cpu_usage_pct = float(input_dict.get("cpu_usage_pct", 0))
    memory_usage_mb = float(input_dict.get("memory_usage_mb", 0))

    raw_log = input_dict.get("error_log", "")
    cleaned_log = clean_log(raw_log)

    risk_score = 0.10

    risk_score += min(previous_failure_rate, 1.0) * 0.25
    risk_score += min(tests_failed / 5, 1.0) * 0.35
    risk_score += min(warnings / 10, 1.0) * 0.15
    risk_score += min(retry_count / 3, 1.0) * 0.10
    risk_score += min(commit_size / 100, 1.0) * 0.05
    risk_score += min(files_changed / 30, 1.0) * 0.05
    risk_score += min(cpu_usage_pct / 100, 1.0) * 0.05
    risk_score += min(memory_usage_mb / 8000, 1.0) * 0.05

    high_risk_keywords = [
        "assertionerror",
        "modulenotfounderror",
        "permission denied",
        "secret",
        "timeout",
        "vulnerability",
        "security",
        "docker build",
        "deployment failed",
        "network",
        "dns",
        "memory",
        "cpu"
    ]

    for keyword in high_risk_keywords:
        if keyword in cleaned_log:
            risk_score += 0.15
            break

    return min(risk_score, 1.0)


def classify_failure_type(raw_log, prediction):
    """
    Classify the likely failure type from the error log.

    If the trained Failure Type Classifier exists, use the .pkl model.
    If it does not exist yet, use keyword-based fallback logic.
    """

    cleaned_log = clean_log(raw_log)

    if not cleaned_log and prediction == "PASS":
        return "None", cleaned_log

    if failure_type_classifier is not None and cleaned_log:
        failure_type = failure_type_classifier.predict(
            [cleaned_log]
        )[0]

        return failure_type, cleaned_log

    failure_type = classify_failure_type_fallback(
        cleaned_log,
        prediction
    )

    return failure_type, cleaned_log


def classify_failure_type_fallback(cleaned_log, prediction):
    """
    Temporary keyword-based failure type logic until Model 2 is trained.
    """

    if not cleaned_log and prediction == "PASS":
        return "None"

    if "assertionerror" in cleaned_log or "test" in cleaned_log:
        return "Test Failure"

    if "modulenotfounderror" in cleaned_log or "no module named" in cleaned_log:
        return "Dependency Error"

    if "docker" in cleaned_log or "build" in cleaned_log:
        return "Build Failure"

    if "deployment" in cleaned_log or "deploy" in cleaned_log:
        return "Deployment Failure"

    if "permission" in cleaned_log or "secret" in cleaned_log or "token" in cleaned_log:
        return "Permission Error"

    if "security" in cleaned_log or "vulnerability" in cleaned_log or "cve" in cleaned_log:
        return "Security Scan Failure"

    if "network" in cleaned_log or "dns" in cleaned_log or "connection" in cleaned_log:
        return "Network Error"

    if "memory" in cleaned_log or "cpu" in cleaned_log or "resource" in cleaned_log:
        return "Resource Exhaustion"

    if "timeout" in cleaned_log or "timed out" in cleaned_log:
        return "Timeout"

    if "yaml" in cleaned_log or "configuration" in cleaned_log or "environment variable" in cleaned_log:
        return "Configuration Error"

    if prediction == "FAIL":
        return "Unknown"

    return "None"


def make_prediction(request_data, database):
    """
    Main prediction service used by FastAPI.
    """

    prediction, risk_score = predict_pipeline_risk(request_data)

    failure_type, cleaned_log = classify_failure_type(
        raw_log=request_data.error_log,
        prediction=prediction
    )

    quality_gate_result = evaluate_quality_gate(
        risk_score=risk_score,
        quality_gate_enabled=request_data.quality_gate_enabled
    )

    recommendation_result = generate_recommendation(
        risk_score=risk_score,
        prediction=prediction,
        failure_type=failure_type,
        raw_log=request_data.error_log,
        cleaned_log=cleaned_log,
        tests_failed=request_data.tests_failed,
        warnings=request_data.warnings
    )

    result = {
        "pipeline_id": request_data.pipeline_id,
        "run_id": request_data.run_id,
        "ci_tool": request_data.ci_tool,
        "repository": request_data.repository,
        "branch": request_data.branch,
        "source": request_data.source,
        "commit_size": request_data.commit_size,
        "files_changed": request_data.files_changed,
        "warnings": request_data.warnings,
        "cpu_usage_pct": request_data.cpu_usage_pct,
        "memory_usage_mb": request_data.memory_usage_mb,
        "retry_count": request_data.retry_count,
        "tests_failed": request_data.tests_failed,
        "build_duration_sec": request_data.build_duration_sec,
        "test_duration_sec": request_data.test_duration_sec,
        "deploy_duration_sec": request_data.deploy_duration_sec,
        "previous_failure_rate": request_data.previous_failure_rate,
        "prediction": prediction,
        "risk_score": risk_score,
        "risk_level": quality_gate_result["risk_level"],
        "failure_type": failure_type,
        "recommendation": recommendation_result["recommendation"],
        "preventive_advice": recommendation_result["preventive_advice"],
        "quality_gate_action": quality_gate_result["action"],
        "threshold_explanation": quality_gate_result["threshold_explanation"],
        "actual_result": request_data.actual_result,
        "raw_log": request_data.error_log,
        "cleaned_log": cleaned_log,
    }

    history_repository = HistoryRepository(
    database
)
    history_repository.save(
    result
)

    response = {
        "pipeline_id": result["pipeline_id"],
        "run_id": result["run_id"],
        "prediction": result["prediction"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "failure_type": result["failure_type"],
        "recommendation": result["recommendation"],
        "preventive_advice": result["preventive_advice"],
        "quality_gate_action": result["quality_gate_action"],
        "threshold_explanation": result["threshold_explanation"],
        "cleaned_log_preview": cleaned_log[:250]
    }

    return response