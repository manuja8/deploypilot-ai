import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import api.auth as auth_module
from api.auth import auth_service, require_admin, require_user, verify_github_key
from api.database import Base
from api.history_repository import HistoryRepository
from api.model_loader import load_models
from api.prediction_service import _get_repository_gate_context, make_prediction
from api.quality_gate import evaluate_quality_gate
from api.recommendation_engine import generate_recommendation
from api.schemas import PredictionRequest


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)
    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_at01_saved_models_load():
    models = load_models()

    assert models["failure_risk_model_loaded"] is True
    assert models["failure_type_classifier_loaded"] is True
    assert models["failure_risk_model"] is not None
    assert models["failure_type_classifier"] is not None


def test_at02_password_and_jwt_authentication():
    class TestUser:
        id = 999
        email = "automated.user@deploypilot.local"
        display_name = "Automated User"
        role = "USER"

    password = "Temp-Automated-Password-2026"
    saved_hash = auth_service.hash_password(password)

    assert saved_hash != password
    assert auth_service.check_password(password, saved_hash) is True
    assert auth_service.check_password("wrong-password", saved_hash) is False

    token = auth_service.create_token(TestUser())
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )
    payload = require_user(credentials)

    assert payload["user_id"] == 999
    assert payload["email"] == TestUser.email
    assert payload["role"] == "USER"


def test_at03_manual_prediction_service(db_session):
    request = PredictionRequest(
        pipeline_id="AT03",
        run_id="AT03_RUN_001",
        ci_tool="GitHub Actions",
        repository="automated-manual-test",
        branch="main",
        source="MANUAL",
        commit_size=45,
        files_changed=8,
        warnings=3,
        tests_failed=1,
        build_duration_sec=900,
        test_duration_sec=500,
        deploy_duration_sec=200,
        cpu_usage_pct=65,
        memory_usage_mb=6000,
        retry_count=1,
        previous_failure_rate=0.2,
        language="Python",
        os="ubuntu-latest",
        cloud_provider="GitHub Hosted",
        error_log="AssertionError expected 200 got 500",
        quality_gate_enabled=True,
        actual_result="FAIL",
    )

    result = make_prediction(request, db_session)

    assert result["prediction"] in {"PASS", "FAIL"}
    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert result["quality_gate_action"] in {"ALLOW", "WARN", "BLOCK"}
    assert result["gate_mode"] == "ENFORCING"
    assert result["cold_start"] is False


def test_at04_prediction_history_storage(db_session):
    repository = HistoryRepository(db_session)

    saved = repository.save(
        {
            "pipeline_id": "AT04",
            "run_id": "AT04_RUN_001",
            "repository": "automated-history-test",
            "source": "MANUAL",
            "prediction": "PASS",
            "risk_score": 0.21,
            "risk_level": "LOW",
            "quality_gate_action": "ALLOW",
            "actual_result": "PASS",
        }
    )

    records = repository.get_all()

    assert saved.id is not None
    assert len(records) == 1
    assert records[0].run_id == "AT04_RUN_001"
    assert records[0].repository == "automated-history-test"
    assert records[0].quality_gate_action == "ALLOW"


def test_at05_quality_gate_boundaries():
    low = evaluate_quality_gate(0.39, True)
    medium = evaluate_quality_gate(0.40, True)
    high = evaluate_quality_gate(0.70, True)
    advisory_high = evaluate_quality_gate(0.70, False, "automated advisory test")

    assert (low["risk_level"], low["action"]) == ("LOW", "ALLOW")
    assert (medium["risk_level"], medium["action"]) == ("MEDIUM", "WARN")
    assert (high["risk_level"], high["action"]) == ("HIGH", "BLOCK")
    assert (advisory_high["risk_level"], advisory_high["action"]) == ("HIGH", "WARN")


def test_at06_repository_cold_start_transition(db_session):
    repository_name = "automated-cold-start-test"

    request = PredictionRequest(
        pipeline_id="AT06",
        run_id="AT06_CURRENT",
        repository=repository_name,
        source="GITHUB_ACTIONS",
        quality_gate_enabled=True,
    )

    before = _get_repository_gate_context(request, db_session)

    assert before["meaningful_history_runs"] == 0
    assert before["cold_start"] is True
    assert before["gate_mode"] == "ADVISORY"
    assert before["effective_gate_enabled"] is False

    repository = HistoryRepository(db_session)
    for index, actual_result in enumerate(["PASS", "FAIL", "PASS"], start=1):
        repository.save(
            {
                "pipeline_id": f"AT06_PREVIOUS_{index}",
                "run_id": f"AT06_PREVIOUS_RUN_{index}",
                "repository": repository_name,
                "source": "GITHUB_ACTIONS",
                "actual_result": actual_result,
            }
        )

    after = _get_repository_gate_context(request, db_session)

    assert after["meaningful_history_runs"] == 3
    assert after["cold_start"] is False
    assert after["gate_mode"] == "ENFORCING"
    assert after["effective_gate_enabled"] is True
    assert after["previous_failure_rate"] == pytest.approx(0.333, abs=0.001)


def test_at07_github_api_key_validation(monkeypatch):
    temporary_key = "deploypilot-automated-local-key"
    monkeypatch.setattr(auth_module, "GITHUB_API_KEY", temporary_key)

    assert verify_github_key(temporary_key) is True

    with pytest.raises(HTTPException) as error:
        verify_github_key("wrong-key")

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid GitHub API key."


def test_at08_dependency_recommendation():
    result = generate_recommendation(
        risk_score=0.82,
        prediction="FAIL",
        failure_type="Dependency Error",
        raw_log="ModuleNotFoundError: No module named pandas",
        cleaned_log="modulenotfounderror no module named pandas",
        tests_failed=0,
        warnings=2,
        actual_result="FAIL",
    )

    assert "dependency" in result["recommendation"].lower()
    assert "pin dependency versions" in result["preventive_advice"].lower()
    assert len(result["explanation"]) > 0


def test_at09_admin_user_access_control():
    admin = {"user_id": 1, "role": "ADMIN"}
    user = {"user_id": 2, "role": "USER"}

    assert require_admin(admin) == admin

    with pytest.raises(HTTPException) as error:
        require_admin(user)

    assert error.value.status_code == 403
    assert error.value.detail == "Administrator access is required."
