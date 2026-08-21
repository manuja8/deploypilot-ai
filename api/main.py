from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from api.auth import auth_service, require_user, verify_github_key
from api.database import Base, engine, get_db
from api.history_repository import HistoryRepository
from api.models import User
from api.prediction_service import loaded_models, make_prediction
from api.schemas import (
    LoginRequest,
    LoginResponse,
    PredictionRequest,
    PredictionResponse,
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="DeployPilot AI API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post(
    "/auth/login",
    response_model=LoginResponse
)
def login(
    request: LoginRequest,
    database: Session = Depends(get_db)
):
    user = (
        database
        .query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not auth_service.check_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "access_token": auth_service.create_token(user),
        "token_type": "bearer",
        "display_name": user.display_name
    }


@app.get("/history")
def history(
    database: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    repository = HistoryRepository(
        database
    )

    return [
        item.to_dict()
        for item in repository.get_all()
    ]


@app.get("/model-status")
def model_status():
    return {
        "failure_risk_model_loaded":
            loaded_models["failure_risk_model_loaded"],

        "failure_type_classifier_loaded":
            loaded_models["failure_type_classifier_loaded"]
    }


@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(
    request: PredictionRequest,
    database: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    return make_prediction(
        request,
        database
    )

@app.post(
    "/github/predict",
    response_model=PredictionResponse
)
def github_predict(
    request: PredictionRequest,
    database: Session = Depends(get_db),
    github_key=Depends(verify_github_key)
):
    request.source = "GITHUB_ACTIONS"

    return make_prediction(
        request,
        database
    )

#uvicorn api.main:app --reload