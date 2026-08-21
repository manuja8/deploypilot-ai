from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from api.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(300), nullable=False)
    display_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    source = Column(
        String(30),
        default="MANUAL"
    )

    pipeline_id = Column(String(100))
    run_id = Column(String(100))
    ci_tool = Column(String(50))
    repository = Column(String(150))
    branch = Column(String(100))

    commit_size = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    tests_failed = Column(Integer, default=0)

    build_duration_sec = Column(Float, default=0)
    test_duration_sec = Column(Float, default=0)
    deploy_duration_sec = Column(Float, default=0)

    cpu_usage_pct = Column(Float, default=0)
    memory_usage_mb = Column(Float, default=0)

    retry_count = Column(Integer, default=0)
    previous_failure_rate = Column(Float, default=0)

    prediction = Column(String(20))
    risk_score = Column(Float)
    risk_level = Column(String(20))
    failure_type = Column(String(100))

    recommendation = Column(Text)
    preventive_advice = Column(Text)

    quality_gate_action = Column(String(20))
    threshold_explanation = Column(Text)

    actual_result = Column(String(20))

    raw_log = Column(Text)
    cleaned_log = Column(Text)

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }