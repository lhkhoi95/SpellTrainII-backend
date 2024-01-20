from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from api.utils.generative_ai import get_word_list_from_AI, get_word_details
from api.models import models
from api.schemas import schemas


def get_word_by_id(db: Session, word_id: int):
    return db.query(models.Word).filter(models.Word.id == word_id).first()


def get_word_list_by_id(db: Session, word_list_id: int):
    return db.query(models.WordList).filter(models.WordList.id == word_list_id).first()


def get_word_lists_by_uid(db: Session, uid: int):
    return db.query(models.WordList).filter(models.WordList.ownerId == uid).all()


def get_word_list_by_title(db: Session, title: str):
    search_title = f"%{title}%"
    return db.query(models.WordList).filter(models.WordList.title.like(search_title)).first()


def create_generative_word_list(db: Session, topic: str, user_id: int):
    try:
        # Try to fetch a list of words from OpenAI API
        word_list = get_word_list_from_AI(
            topic=topic)

        # Create a new word list
        db_word_list = models.WordList(title=topic, ownerId=user_id)
        db.add(db_word_list)
        db.flush()

        for word in word_list:
            word_to_add = {
                'word': word,
                'definition': '',
                'rootOrigin': '',
                'usage': '',
                'languageOrigin': '',
                'partsOfSpeech': '',
                'alternatePronunciation': ''
            }
            db_word = models.Word(**word_to_add)
            db.add(db_word)
            db.flush()
            db_word_list.words.append(db_word)
        db.commit()
        db.refresh(db_word_list)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity Error")

    return db_word_list


def update_word_list(db: Session, word_list: schemas.WordListUpdate):
    db_word_list = get_word_list_by_id(db, word_list.id)

    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    db_word_list.title = word_list.title
    db.commit()
    db.refresh(db_word_list)

    return db_word_list


def delete_word_list(db: Session, word_list_id: int):
    db_word_list = get_word_list_by_id(db, word_list_id)

    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    db.delete(db_word_list)
    db.commit()

    return db_word_list


def get_more_words(db: Session, word_list_id: int):
    # get topic
    db_word_list = get_word_list_by_id(db, word_list_id)
    topic = db_word_list.title
    existing_words = []
    # get existing words
    for word in db_word_list.words:
        existing_words.append(word.word)

    # get more words
    additional_word_list = get_word_list_from_AI(
        topic=topic, get_more=True, existing_words=existing_words)

    # add more words to db
    for word in additional_word_list:
        word_to_add = dict()
        word_to_add['word'] = word
        word_to_add['definition'] = ''
        word_to_add['rootOrigin'] = ''
        word_to_add['usage'] = ''
        word_to_add['languageOrigin'] = ''
        word_to_add['partsOfSpeech'] = ''
        word_to_add['alternatePronunciation'] = ''
        db_word = models.Word(**word_to_add)
        db.add(db_word)
        db.flush()
        db_word_list.words.append(db_word)
    db.commit()
    db.refresh(db_word_list)

    return db_word_list


def get_word_info(db: Session, word_id: int):
    db_word = get_word_by_id(db, word_id)
    db_word_list = get_word_list_by_id(db, db_word.wordListId)
    topic = db_word_list.title

    word_info: schemas.WordInfo = get_word_details(
        db_word.word, topic)

    db_word.definition = word_info.definition
    db_word.rootOrigin = word_info.rootOrigin
    db_word.usage = word_info.usage
    db_word.languageOrigin = word_info.languageOrigin
    db_word.partsOfSpeech = word_info.partsOfSpeech
    db_word.alternatePronunciation = word_info.alternatePronunciation
    db.commit()
    db.refresh(db_word)

    return db_word


def update_word(db: Session, word: schemas.Word) -> schemas.Word:
    db_word = get_word_by_id(db, word.id)

    if db_word is None:
        raise HTTPException(status_code=404, detail="Word not found")

    db_word.word = word.word
    db_word.definition = word.definition
    db_word.rootOrigin = word.rootOrigin
    db_word.usage = word.usage
    db_word.languageOrigin = word.languageOrigin
    db_word.partsOfSpeech = word.partsOfSpeech
    db_word.alternatePronunciation = word.alternatePronunciation
    db.commit()
    db.refresh(db_word)

    return schemas.Word.model_validate(db_word)


def delete_words(db: Session, word_ids: List[int]):
    deleted_words = []

    try:
        for word_id in word_ids:
            db_word = get_word_by_id(db, word_id)
            if db_word is None:
                raise HTTPException(status_code=404, detail="Word not found")
            db.delete(db_word)
            db.flush()
            deleted_words.append(db_word)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    return deleted_words
