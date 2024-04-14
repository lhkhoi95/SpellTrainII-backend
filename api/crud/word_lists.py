from typing import List
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from api.utils.SpellTrainII_AI import SpellTrain2AI
from api.models import models
from api.schemas import schemas
from api.utils.helpers import delete_audio_file, get_audio_url, word_dict
from thefuzz import fuzz


def get_all_words(db: Session):
    return db.query(models.Word).all()


def get_word_by_id(db: Session, word_id: int):
    return db.query(models.Word).filter(models.Word.id == word_id).first()


def get_word_list_by_id(db: Session, word_list_id: int, user_id: int = None):
    if user_id:
        return db.query(models.WordList).filter(models.WordList.id == word_list_id, models.WordList.ownerId == user_id).first()
    else:
        return db.query(models.WordList).filter(models.WordList.id == word_list_id).first()


def get_word_lists_by_uid(db: Session, uid: int):
    return db.query(models.WordList).filter(models.WordList.ownerId == uid).all()


def get_user_word_list_by_title(db: Session, title: str, uid: int):
    word_lists = db.query(models.WordList).filter(
        models.WordList.ownerId == uid).all()
    for word_list in word_lists:
        similarity = fuzz.ratio(title.lower(), word_list.title.lower())
        if similarity >= 80:
            return word_list
    return None


def get_word_list_by_title(db: Session, title: str):
    word_lists = db.query(models.WordList).all()
    for word_list in word_lists:
        similarity = fuzz.ratio(title.lower(), word_list.title.lower())
        if similarity >= 80:
            return word_list
    return None


def create_generative_word_list(db: Session, topic: str, user_id: int):
    try:
        # Try to fetch a list of words from the AI
        spelltrain2AI = SpellTrain2AI()
        word_list = spelltrain2AI.get_word_list(topic=topic)

        # Create a new word list
        db_word_list = models.WordList(title=topic, ownerId=user_id)
        db.add(db_word_list)
        db.flush()

        # Add words to the word list
        for word in word_list:
            word_to_add = word_dict(word)
            db_word = models.Word(**word_to_add)
            db_word.audioUrl = get_audio_url(db_word.word)
            db.add(db_word)
            db.flush()
            db_word_list.words.append(db_word)
        db.commit()
        db.refresh(db_word_list)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity Error")

    return db_word_list


def update_custom_word_list(db: Session, word_list_id: str, word_objs: List[schemas.CustomWord]):
    try:
        # Get existing word list from db
        existing_word_list_db = get_word_list_by_id(
            db=db, word_list_id=word_list_id)

        # extract all the words and convert to lower case
        words_db = [word_obj.word.lower()
                    for word_obj in existing_word_list_db.words]

        # Add non-duplicated words to the existing word list.
        for word_obj in word_objs:
            if word_obj.word.lower() not in words_db:
                word_to_add = models.Word(
                    **word_obj.model_dump(), isAIGenerated=False)
                word_to_add.audioUrl = get_audio_url(word_to_add.word)

                db.add(word_to_add)
                db.flush()
                existing_word_list_db.words.append(word_to_add)
        db.commit()
        db.refresh(existing_word_list_db)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity Error")

    return existing_word_list_db


def create_custom_word_list(db: Session, topic: str, user_id: int, words: List[schemas.CustomWord]):
    try:
        # Create a new word list
        db_word_list = models.WordList(
            title=topic, ownerId=user_id, isAIGenerated=False)
        db.add(db_word_list)
        db.flush()

        # Add custom words, if any.
        if words:
            for word_to_add in words:
                db_word = models.Word(
                    **word_to_add.model_dump(), isAIGenerated=False)
                db_word.audioUrl = get_audio_url(db_word.word)
                db.add(db_word)
                db.flush()
                db_word_list.words.append(db_word)
        db.commit()
        db.refresh(db_word_list)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity Error")

    return db_word_list


def get_more_words(db: Session, word_list_id: int):
    existing_words = []
    spelltrain2AI = SpellTrain2AI()

    # Get the topic of the word list
    db_word_list = get_word_list_by_id(db, word_list_id)
    topic = db_word_list.title

    # Get existing words in database
    for word in db_word_list.words:
        existing_words.append(word.word)

    # Get additional words from AI
    additional_word_list = spelltrain2AI.get_word_list(
        topic=topic, existing_words=existing_words)

    # Add more words to db
    for word in additional_word_list:
        word_to_add = word_dict(word)
        db_word = models.Word(**word_to_add)
        db_word.audioUrl = get_audio_url(db_word.word)
        db.add(db_word)
        db.flush()
        db_word_list.words.append(db_word)
    db.commit()
    db.refresh(db_word_list)

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

    # Extract audio urls
    audio_urls = [word.audioUrl for word in db_word_list.words]

    db.delete(db_word_list)
    db.commit()

    # Delete audio files
    if audio_urls:
        delete_audio_file(audio_urls)

    return db_word_list


def get_word_info(db: Session, word_id: int):
    spelltrain2AI = SpellTrain2AI()

    db_word = get_word_by_id(db, word_id)
    db_word_list = get_word_list_by_id(db, db_word.wordListId)
    topic = db_word_list.title
    word_by_AI = spelltrain2AI.get_word_details(db_word.word, topic)

    db_word.definition = word_by_AI.definition
    db_word.rootOrigin = word_by_AI.rootOrigin
    db_word.usage = word_by_AI.usage
    db_word.languageOrigin = word_by_AI.languageOrigin
    db_word.partsOfSpeech = word_by_AI.partsOfSpeech
    db_word.alternatePronunciation = word_by_AI.alternatePronunciation.encode(
        'utf-8')

    db.commit()
    db.refresh(db_word)

    return db_word


def add_words(db: Session, words: List[schemas.Word]):
    try:
        added_words = []
        for word in words:
            word_to_add = word_dict(word.word)
            db_word = models.Word(
                **word_to_add, wordListId=word.wordListId, isAIGenerated=False)
            db_word.audioUrl = get_audio_url(db_word.word)
            db.add(db_word)
            db.flush()
            added_words.append(db_word)

        db.commit()
        db.refresh(added_words[0])

        # Get the word list
        db_word_list = get_word_list_by_id(db, words[0].wordListId)

        return db_word_list
    except Exception as e:
        db.rollback()
        raise e


def update_words(db: Session, words_to_update: List[schemas.Word]) -> List[schemas.Word]:
    updated_words = []
    try:
        for word in words_to_update:
            db_word = get_word_by_id(db, word.id)

            if db_word is None:
                raise HTTPException(
                    status_code=404, detail=f"Word ID {word.id} not found")

            db_word.word = word.word
            db_word.definition = word.definition
            db_word.rootOrigin = word.rootOrigin
            db_word.usage = word.usage
            db_word.languageOrigin = word.languageOrigin
            db_word.partsOfSpeech = word.partsOfSpeech
            db_word.alternatePronunciation = word.alternatePronunciation
            db.commit()
            db.refresh(db_word)
            updated_words.append(schemas.Word.model_validate(db_word))

        return updated_words
    except Exception as e:
        db.rollback()
        raise e


def delete_words(db: Session, word_ids: List[int]):
    deleted_words = []
    audio_urls = []

    try:
        for word_id in word_ids:
            db_word = get_word_by_id(db, word_id)
            if db_word is None:
                raise HTTPException(
                    status_code=404, detail=f"Word ID {word_id} not found")

            db.delete(db_word)
            db.flush()
            deleted_words.append(db_word)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    audio_urls = [word.audioUrl for word in deleted_words]
    delete_audio_file(audio_urls)

    return deleted_words
