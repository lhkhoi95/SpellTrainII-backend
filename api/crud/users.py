
import hashlib
from sqlalchemy.orm import Session
from api.models import models
from api.schemas import schemas


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed = hashlib.pbkdf2_hmac(
        'sha256', user.password.encode('utf-8'), b'salt', 100000)
    db_user = models.User(name=user.name, email=user.email,
                          phone=user.phone, wordLists=user.wordLists, password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: str, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    fields_to_update = user.model_dump(exclude_unset=True)

    # Update the fields
    for key, value in fields_to_update.items():
        # If key is password, hash the value
        if key == 'password':
            value = hashlib.pbkdf2_hmac(
                'sha256', value.encode('utf-8'), b'salt', 100000)
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(db_user)
    db.commit()
    return db_user
