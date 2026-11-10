import hashlib
import os
import secrets
import time
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash
from sqlalchemy import ForeignKey, String, create_engine, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str]


class LoginSession(Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    csrf: Mapped[str]
    expires_at: Mapped[int]


engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///" + str(Path(__file__).with_name("app.db"))), connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
app = FastAPI(title="WTaM API")
passwords = PasswordHash.recommended()
dummy_hash = passwords.hash(secrets.token_urlsafe(32))
secure_cookie = os.getenv("COOKIE_SECURE", "false").lower() == "true"
cookie_name = "wtam_session"
session_seconds = 60 * 60 * 24 * 7


def db_session():
    with Session(engine) as db:
        yield db


def digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def current_session(request: Request, db: Session = Depends(db_session)):
    session = db.get(LoginSession, digest(request.cookies.get(cookie_name, "")))
    if not session or session.expires_at <= time.time():
        raise HTTPException(401, "Please log in.")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        if not secrets.compare_digest(request.headers.get("X-CSRF-Token", ""), session.csrf):
            raise HTTPException(403, "Invalid CSRF token.")
    return session


@app.middleware("http")
async def check_origin(request: Request, call_next):
    # Custom headers require a same-origin request or a successful CORS preflight.
    # No cross-origin access is enabled; Vite proxies /api during development.
    if request.method not in {"GET", "HEAD", "OPTIONS"} and request.url.path.startswith("/api/"):
        if request.headers.get("X-Requested-With") != "WTaM":
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Missing request header."}, status_code=403)
    return await call_next(request)


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class Registration(Credentials):
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=10, max_length=128)


def user_data(user: User):
    return {"id": user.id, "name": user.name, "email": user.email}


def sign_in(user: User, request: Request, response: Response, db: Session):
    old = request.cookies.get(cookie_name)
    if old:
        db.execute(delete(LoginSession).where(LoginSession.token_hash == digest(old)))
    db.execute(delete(LoginSession).where(LoginSession.expires_at <= int(time.time())))
    token = secrets.token_urlsafe(32)
    session = LoginSession(token_hash=digest(token), user_id=user.id, csrf=secrets.token_urlsafe(32), expires_at=int(time.time()) + session_seconds)
    db.add(session)
    db.commit()
    response.set_cookie(cookie_name, token, httponly=True, secure=secure_cookie, samesite="lax", max_age=session_seconds, path="/")
    response.headers["Cache-Control"] = "no-store"
    return {"user": user_data(user), "csrf_token": session.csrf}


@app.post("/api/auth/register", status_code=201)
def register(data: Registration, request: Request, response: Response, db: Session = Depends(db_session)):
    name = data.name.strip()
    if not name:
        raise HTTPException(422, "Name cannot be blank.")
    user = User(name=name, email=str(data.email).lower(), password_hash=passwords.hash(data.password))
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "An account with that email already exists.")
    return sign_in(user, request, response, db)


@app.post("/api/auth/login")
def login(data: Credentials, request: Request, response: Response, db: Session = Depends(db_session)):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    valid = passwords.verify(data.password, user.password_hash if user else dummy_hash)
    if not user or not valid:
        raise HTTPException(401, "Invalid email or password.")
    return sign_in(user, request, response, db)


@app.get("/api/auth/me")
def me(response: Response, session: LoginSession = Depends(current_session), db: Session = Depends(db_session)):
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(401, "Please log in.")
    response.headers["Cache-Control"] = "no-store"
    return {"user": user_data(user), "csrf_token": session.csrf}


@app.post("/api/auth/logout", status_code=204)
def logout(response: Response, session: LoginSession = Depends(current_session), db: Session = Depends(db_session)):
    db.delete(session)
    db.commit()
    response.delete_cookie(cookie_name, path="/", secure=secure_cookie, httponly=True, samesite="lax")


dist = Path(__file__).parent.parent / "frontend" / "dist"
if dist.is_dir():
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
