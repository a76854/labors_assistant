"""
用户认证服务 - 密码哈希 / JWT 签发与校验
纯标准库实现，无第三方依赖
"""

import base64
import hashlib
import hmac
import json
import os
import time
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.db.database import get_db
from backend.db.models import User

settings = get_settings()

_PBKDF2_ITERATIONS = 100_000
_ALGORITHM = "HS256"


# ============================================================================
# 密码哈希（PBKDF2-HMAC-SHA256）
# ============================================================================

def hash_password(password: str) -> str:
    """生成密码哈希，格式: pbkdf2_sha256$iterations$salt$hash"""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return "$".join(
        [
            "pbkdf2_sha256",
            str(_PBKDF2_ITERATIONS),
            _b64(salt),
            _b64(digest),
        ]
    )


def verify_password(password: str, password_hash: str) -> bool:
    """校验密码与哈希是否匹配"""
    try:
        _, iterations_str, salt_b64, hash_b64 = password_hash.split("$")
        iterations = int(iterations_str)
        salt = _unb64(salt_b64)
        expected = _unb64(hash_b64)
    except (ValueError, TypeError):
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(digest, expected)


# ============================================================================
# JWT 签发与校验（HS256，标准库实现）
# ============================================================================

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(user: User, expires_minutes: int | None = None) -> str:
    """签发 JWT access token"""
    expires_minutes = expires_minutes or settings.access_token_expire_minutes
    now = int(time.time())
    header = {"alg": _ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "iat": now,
        "exp": now + expires_minutes * 60,
    }
    header_b64 = _b64(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(
        settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    return f"{header_b64}.{payload_b64}.{_b64(signature)}"


def decode_access_token(token: str) -> dict | None:
    """解析并校验 JWT，返回 payload；无效或过期返回 None"""
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected = hmac.new(
            settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        if not hmac.compare_digest(expected, _unb64(signature_b64)):
            return None
        payload = json.loads(_unb64(payload_b64))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


# ============================================================================
# FastAPI 依赖
# ============================================================================

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从 Authorization: Bearer <token> 中解析当前登录用户。"""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录或登录已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise unauthorized

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise unauthorized
    return user


def get_current_lawyer(current_user: User = Depends(get_current_user)) -> User:
    """仅允许律师角色访问。"""
    if current_user.role != "lawyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要律师身份",
        )
    return current_user
