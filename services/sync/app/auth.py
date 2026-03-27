"""Authentication helpers – JWT sessions + bcrypt passwords."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import Request, Response

from app import shared

SECRET_KEY = os.environ.get('JWT_SECRET', 'whisper-studio-dev-secret-change-me')
ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = 72
COOKIE_NAME = 'ws_session'


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: str, username: str, role: str) -> str:
    payload = {
        'sub': user_id,
        'username': username,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_current_user(request: Request) -> dict[str, Any] | None:
    """Extract user from session cookie. Returns None if not authenticated."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    user = shared.db.get_user(payload['sub'])
    return user


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=TOKEN_EXPIRE_HOURS * 3600,
        httponly=True,
        samesite='lax',
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME)


def ensure_admin_exists() -> None:
    """Create default admin user if no users exist (first-run setup)."""
    if shared.db.user_count() > 0:
        return
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
    now = datetime.now(timezone.utc).isoformat()

    # Ensure default space exists
    if not shared.db.get_space('default'):
        shared.db.create_space({
            'space_id': 'default',
            'name': 'Whisper Studio',
            'tagline': 'Seven Kingdoms · Content Production',
            'created_at': now,
        })

    shared.db.create_user({
        'user_id': str(uuid.uuid4()),
        'username': 'admin',
        'display_name': 'Admin',
        'email': '',
        'password_hash': hash_password(admin_password),
        'role': 'admin',
        'space_id': 'default',
        'created_at': now,
    })
    print(f'[auth] Default admin user created (password: {admin_password})')
