from passlib.context import CryptContext
from sqlalchemy.orm import Session
from api.models import models
from api.schemas import schemas
from api.utils.helpers import delete_audio_file

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed = pwd_context.hash(user.password)
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
            value = pwd_context.hash(value)
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    # Extract the audio files from the words
    for word_list in db_user.wordLists:
        for word in word_list.words:
            if word.audioUrl:
                delete_audio_file(word.audioUrl)
    db.delete(db_user)
    db.commit()
    return db_user
