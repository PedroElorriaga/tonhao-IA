import os
import uuid

from dotenv import load_dotenv
load_dotenv()  # load .env before any other imports read os.environ

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.database.sqlite_config import get_db
from src.modules.auth.dependencies import (
    COOKIE_NAME,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from src.modules.auth.model import User
from src.modules.auth.schema import LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# ── Google OAuth config ────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
GOOGLE_REDIRECT_URI = f"{BACKEND_URL}/auth/google/callback"

_COOKIE_OPTS = dict(
    key=COOKIE_NAME,
    httponly=True,
    samesite="lax",
    secure=os.getenv("ENVIRONMENT", "development") == "production",
    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    path="/",
)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        role="client",  # default role for self-registered users
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role)
    response.set_cookie(value=token, **_COOKIE_OPTS)
    return user


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id, user.role)
    response.set_cookie(value=token, **_COOKIE_OPTS)
    return user


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.get("/google")
def google_login():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth is not configured")

    params = (
        f"client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
    )
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")


@router.get("/google/callback")
def google_callback(code: str, response: Response, db: Session = Depends(get_db)):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth is not configured")

    # Exchange code for tokens
    with httpx.Client() as client:
        token_resp = client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange Google code")

    id_token = token_resp.json().get("id_token")

    # Verify id_token via Google's tokeninfo endpoint
    with httpx.Client() as client:
        info_resp = client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
    if info_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    info = info_resp.json()
    google_id = info.get("sub")
    email = info.get("email")
    name = info.get("name") or email

    # Find or create user
    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_id = google_id  # link Google to existing account
        else:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                name=name,
                google_id=google_id,
                role="client",
            )
            db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role)
    redirect = RedirectResponse(url=FRONTEND_URL)
    redirect.set_cookie(value=token, **_COOKIE_OPTS)
    return redirect
