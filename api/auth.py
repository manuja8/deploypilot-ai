import hashlib
import hmac
import os
import secrets

import jwt

from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


load_dotenv()

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "deploypilot-local-secret"
)

GITHUB_API_KEY = os.getenv(
    "GITHUB_API_KEY",
    "deploypilot-github-local-key"
)

security = HTTPBearer()


class AuthService:

    def hash_password(self, password):
        salt = secrets.token_hex(16)

        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000
        ).hex()

        return f"{salt}${hashed}"

    def check_password(self, password, saved_password):
        salt, saved_hash = saved_password.split("$")

        check_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000
        ).hex()

        return hmac.compare_digest(
            check_hash,
            saved_hash
        )

    def create_token(self, user):
        payload = {
            "user_id": user.id,
            "email": user.email,
            "name": user.display_name,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(hours=8)
        }

        return jwt.encode(
            payload,
            JWT_SECRET,
            algorithm="HS256"
        )


auth_service = AuthService()


def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        return jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=["HS256"]
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired login."
        )


def require_admin(current_user=Depends(require_user)):
    if current_user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Administrator access is required."
        )

    return current_user


def verify_github_key(
    x_api_key: str = Header(...)
):
    if not hmac.compare_digest(
        x_api_key,
        GITHUB_API_KEY
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid GitHub API key."
        )

    return True
