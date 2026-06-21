from pathlib import Path

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FAILURE_RISK_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "failure_risk_model.pkl"
)

FAILURE_TYPE_CLASSIFIER_PATH = (
    PROJECT_ROOT
    / "models"
    / "failure_type_classifier.pkl"
)


def load_model_if_exists(model_path):
    """
    Load a joblib model if the file exists.
    If the model is not trained yet, return None.
    """

    if model_path.exists():
        return joblib.load(model_path)

    return None


def load_models():
    """
    Load all saved ML models.

    During the current MVP stage, the .pkl files may not exist yet.
    In that case, FastAPI will use fallback logic inside prediction_service.py.
    """

    failure_risk_model = load_model_if_exists(
        FAILURE_RISK_MODEL_PATH
    )

    failure_type_classifier = load_model_if_exists(
        FAILURE_TYPE_CLASSIFIER_PATH
    )

    return {
        "failure_risk_model": failure_risk_model,
        "failure_type_classifier": failure_type_classifier,
        "failure_risk_model_path": str(FAILURE_RISK_MODEL_PATH),
        "failure_type_classifier_path": str(FAILURE_TYPE_CLASSIFIER_PATH),
        "failure_risk_model_loaded": failure_risk_model is not None,
        "failure_type_classifier_loaded": failure_type_classifier is not None
    }