from fastapi import FastAPI

from api.prediction_service import loaded_models, make_prediction
from api.schemas import PredictionRequest, PredictionResponse


app = FastAPI(
    title="DeployPilot AI API",
    description="CI/CD Pipeline Failure Prediction and Risk Control System",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "DeployPilot AI API is running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DeployPilot AI API"
    }


@app.get("/model-status")
def model_status():
    return {
        "failure_risk_model_loaded": loaded_models["failure_risk_model_loaded"],
        "failure_type_classifier_loaded": loaded_models["failure_type_classifier_loaded"],
        "failure_risk_model_path": loaded_models["failure_risk_model_path"],
        "failure_type_classifier_path": loaded_models["failure_type_classifier_path"],
        "note": "If models are not loaded, fallback MVP logic is used."
    }


@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(request: PredictionRequest):
    return make_prediction(request)

#uvicorn api.main:app --reload