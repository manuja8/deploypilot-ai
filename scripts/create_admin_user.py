import os

from api.auth import auth_service
from api.database import Base, SessionLocal, engine
from api.models import User


Base.metadata.create_all(
    bind=engine
)

database = SessionLocal()

email = os.getenv(
    "ADMIN_EMAIL",
    "admin@deploypilot.ai"
)

password = os.getenv(
    "ADMIN_PASSWORD",
    "deploypilot123"
)

name = os.getenv(
    "ADMIN_NAME",
    "DeployPilot Admin"
)


existing_user = (
    database
    .query(User)
    .filter(User.email == email)
    .first()
)


if existing_user:
    print("Admin user already exists.")

else:
    admin_user = User(
        email=email,
        password_hash=auth_service.hash_password(password),
        display_name=name
    )

    database.add(admin_user)
    database.commit()

    print("Admin user created.")
    print("Email:", email)


database.close()