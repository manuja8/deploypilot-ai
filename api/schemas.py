from typing import Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    pipeline_id: str = Field(default="manual_pipeline_001")
    run_id: str = Field(default="manual_run_001")
    ci_tool: str = Field(default="GitHub Actions")
    repository: str = Field(default="deploypilot-demo")
    branch: str = Field(default="dev")

    commit_size: int = Field(default=0, ge=0)
    files_changed: int = Field(default=0, ge=0)
    warnings: int = Field(default=0, ge=0)
    tests_failed: int = Field(default=0, ge=0)

    build_duration_sec: float = Field(default=0, ge=0)
    test_duration_sec: float = Field(default=0, ge=0)
    deploy_duration_sec: float = Field(default=0, ge=0)

    cpu_usage_pct: float = Field(default=0, ge=0)
    memory_usage_mb: float = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)
    previous_failure_rate: float = Field(default=0, ge=0, le=1)

    language: str = Field(default="Python")
    os: str = Field(default="ubuntu-latest")
    cloud_provider: str = Field(default="GitHub Hosted")

    error_log: Optional[str] = Field(default="")
    quality_gate_enabled: bool = Field(default=True)

    actual_result: Optional[str] = Field(default="")


class PredictionResponse(BaseModel):
    pipeline_id: str
    run_id: str
    prediction: str
    risk_score: float
    risk_level: str
    failure_type: str
    recommendation: str
    preventive_advice: str
    quality_gate_action: str
    threshold_explanation: str
    cleaned_log_preview: str