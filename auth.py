"""
Authentication utilities for Cal Tracker.
Provides password hashing, JWT token issuance, and FastAPI dependency
for extracting the current user ID from the Authorization header.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

from config import settings
import database

router = APIRouter()

# Cryptographic context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme for extracting Bearer token
bearer_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    """Create a JWT token containing the user_id.
    Token lifetime defaults to 1 day.
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(days=1))
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

def decode_access_token(token: str) -> int:
    """Decode a JWT token and return the embedded user_id.
    Raises HTTPException(401) on failure.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> int:
    """FastAPI dependency that returns the current user ID.
    Expects an Authorization header with a Bearer token.
    """
    return decode_access_token(credentials.credentials)

@router.post("/api/register")
async def register(request: Request):
    """Register a new user with username and password.
    Returns the newly created user_id.
    """
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    # Check if user exists
    conn = database.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already taken")
    password_hash = hash_password(password)
    cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"user_id": user_id}

@router.post("/api/login")
async def login(request: Request):
    """Authenticate a user and return a JWT access token."""
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    conn = database.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row or not verify_password(password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(row["id"])
    return {"access_token": token}
