from jose import jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from api.crud.users import get_user_by_email
from passlib.context import CryptContext
from api.schemas import schemas
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Set expiration to 1 month
        expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv(
        "SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))

    return encoded_jwt


def authenticate_user(db: Session, user: schemas.UserCreate):
    plaintext = user.password
    user_db = get_user_by_email(db=db, email=user.email)
    # If user is not found or passwords are unmatched, return False
    if user_db is None:
        return False
    if not pwd_context.verify(secret=plaintext, hash=user_db.password):
        return False
    return True
