import os
import sys

from pathlib import Path


# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from api.auth import auth_service
from api.database import (
    Base,
    SessionLocal,
    engine,
    ensure_user_role_schema,
)
from api.models import User


Base.metadata.create_all(bind=engine)

# Safely add the role column to older databases.
ensure_user_role_schema()


email = os.getenv(
    "ADMIN_EMAIL",
    "admin@deploypilot.ai"
).strip().lower()

password = os.getenv(
    "ADMIN_PASSWORD",
    "deploypilot123"
)

name = os.getenv(
    "ADMIN_NAME",
    "DeployPilot Admin"
)


database = SessionLocal()

try:
    existing_user = (
        database
        .query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        existing_user.display_name = name
        existing_user.password_hash = auth_service.hash_password(password)
        existing_user.role = "ADMIN"
        existing_user.is_active = True

        database.commit()

        print("Admin user already exists.")
        print("Admin account updated and configured as ADMIN.")

    else:
        admin_user = User(
            email=email,
            password_hash=auth_service.hash_password(password),
            display_name=name,
            role="ADMIN",
            is_active=True
        )

        database.add(admin_user)
        database.commit()

        print("Admin user created and configured as ADMIN.")

    print("Email:", email)

finally:
    database.close()