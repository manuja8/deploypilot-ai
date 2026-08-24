import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.auth import (
    auth_service,
    require_admin,
    require_user,
    verify_github_key,
)
from api.database import Base, engine, ensure_user_role_schema, get_db
from api.history_repository import HistoryRepository
from api.models import User
from api.prediction_service import loaded_models, make_prediction
from api.schemas import (
    AdminUserCreate,
    AdminUserResponse,
    AdminUserUpdate,
    LoginRequest,
    LoginResponse,
    PredictionRequest,
    PredictionResponse,
)


Base.metadata.create_all(
    bind=engine
)
ensure_user_role_schema()


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

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]


def user_to_response(user):
    return {
        "id": user.id,
        "display_name": user.display_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


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
    normalized_email = request.email.strip().lower()

    user = (
        database
        .query(User)
        .filter(func.lower(User.email) == normalized_email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="This account is inactive."
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
        "display_name": user.display_name,
        "role": user.role
    }


@app.get(
    "/admin/users",
    response_model=list[AdminUserResponse]
)
def list_users(
    database: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    users = (
        database
        .query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return [
        user_to_response(user)
        for user in users
    ]


@app.post(
    "/admin/users",
    response_model=AdminUserResponse,
    status_code=201
)
def create_user(
    request: AdminUserCreate,
    database: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    normalized_email = request.email.strip().lower()

    existing_user = (
        database
        .query(User)
        .filter(func.lower(User.email) == normalized_email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    user = User(
        email=normalized_email,
        display_name=request.display_name.strip(),
        password_hash=auth_service.hash_password(request.password),
        role=request.role,
        is_active=True
    )

    database.add(user)
    database.commit()
    database.refresh(user)

    return user_to_response(user)


@app.put(
    "/admin/users/{user_id}",
    response_model=AdminUserResponse
)
def update_user(
    user_id: int,
    request: AdminUserUpdate,
    database: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    user = (
        database
        .query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User account not found."
        )

    if request.email is not None:
        normalized_email = request.email.strip().lower()

        duplicate = (
            database
            .query(User)
            .filter(
                func.lower(User.email) == normalized_email,
                User.id != user_id
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="An account with this email already exists."
            )

        user.email = normalized_email

    if request.display_name is not None:
        user.display_name = request.display_name.strip()

    if request.password is not None:
        user.password_hash = auth_service.hash_password(
            request.password
        )

    if request.role is not None:
        if (
            user.id == current_user.get("user_id")
            and request.role != "ADMIN"
        ):
            raise HTTPException(
                status_code=400,
                detail="You cannot remove your own administrator role."
            )

        user.role = request.role

    database.commit()
    database.refresh(user)

    return user_to_response(user)


@app.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    database: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    if user_id == current_user.get("user_id"):
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account."
        )

    user = (
        database
        .query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User account not found."
        )

    database.delete(user)
    database.commit()

    return {
        "message": "User account deleted successfully."
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


@app.get("/model-metrics")
def model_metrics():

    risk_metrics_path = (
        PROJECT_ROOT
        / "models"
        / "failure_risk_metrics.json"
    )

    failure_type_metrics_path = (
        PROJECT_ROOT
        / "models"
        / "failure_type_metrics.json"
    )

    risk_metrics = None
    failure_type_metrics = None

    if risk_metrics_path.exists():
        with open(
            risk_metrics_path,
            "r"
        ) as file:

            risk_metrics = json.load(file)

    if failure_type_metrics_path.exists():
        with open(
            failure_type_metrics_path,
            "r"
        ) as file:

            failure_type_metrics = json.load(file)

    return {
        "failure_risk_metrics":
            risk_metrics,

        "failure_type_metrics":
            failure_type_metrics
    }


# uvicorn api.main:app --reload
