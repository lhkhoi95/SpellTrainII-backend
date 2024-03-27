import re
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Annotated, List
from api.auth.auth_bearer import RequiredLogin
from api.crud import word_lists as crud
from api.dependencies import get_db
from api.schemas.schemas import CustomWordList, WordCreate, WordList, Word, WordListUpdate
from api.utils.SpellTrainII_AI import SpellTrain2AI

router = APIRouter(
    prefix="/word-lists",
    tags=["word-lists"],
)


@router.get("/", response_model=WordList)
async def create_generative_word_list(topic: Annotated[str, Query(min_length=2)], db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    sanitized_topic = re.sub(r'\s+', ' ', topic).strip().title()
    spelltrain2AI = SpellTrain2AI()

    # If topic is invalid, raise an exception with the reason
    evaluated_topic = spelltrain2AI.evaluate_topic(sanitized_topic)
    if not evaluated_topic.isValid:
        raise HTTPException(
            status_code=400, detail=evaluated_topic.reason)

    # Check for repeated word list.
    word_list_exists = crud.get_user_word_list_by_title(
        db=db, title=sanitized_topic, uid=user_id)
    if word_list_exists:
        return word_list_exists

    # Ask AI models to generate one.
    return crud.create_generative_word_list(db=db, topic=sanitized_topic, user_id=user_id)


@router.put("/", response_model=WordList)
async def create_custom_word_list(custom_word_list: CustomWordList, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    sanitized_topic = re.sub(
        r'\s+', ' ', custom_word_list.title).strip().title()
    words = custom_word_list.words

    spelltrain2AI = SpellTrain2AI()

    # If topic is invalid, raise an exception with the reason
    evaluated_topic = spelltrain2AI.evaluate_topic(sanitized_topic)
    if not evaluated_topic.isValid:
        raise HTTPException(
            status_code=400, detail=evaluated_topic.reason)

    # If words are not empty, validate each word
    if words:
        for word in words:
            result = spelltrain2AI.evaluate_word_topic(
                word=word.word, topic=sanitized_topic)
            if not result.isValid:
                raise HTTPException(
                    status_code=400, detail=f"{word.word} is not a valid word.")

    # If word list exists, try to add words to the existing one but ignore duplicate words.
    word_list_exists = crud.get_user_word_list_by_title(
        db=db, title=sanitized_topic, uid=user_id)
    if word_list_exists:
        return crud.update_custom_word_list(db=db, word_list_id=word_list_exists.id, word_objs=words)

    # Create a new word list
    return crud.create_custom_word_list(db=db, topic=sanitized_topic, user_id=user_id, words=words)


@router.patch("/", response_model=WordList)
async def update_word_list_title(word_list: WordListUpdate, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    # Check if word_list_id exists
    db_word_list = crud.get_word_list_by_id(
        db, word_list_id=word_list.id, user_id=user_id)
    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    # If title is unchanged, return the word list
    if db_word_list.title.lower() == word_list.title.lower():
        return db_word_list

    # Check for repeated title.
    word_list_exists = crud.get_user_word_list_by_title(
        db=db, title=word_list.title, uid=user_id)
    if word_list_exists:
        raise HTTPException(
            status_code=400, detail="Word list with the same title already exists.")

    # Validate the new title
    spelltrain2AI = SpellTrain2AI()
    result = spelltrain2AI.evaluate_topic(word_list.title)
    if not result.isValid:
        raise HTTPException(
            status_code=400, detail=result.reason)

    # For each word in the word list, check if the word is related to the new title
    for word in db_word_list.words:
        result = spelltrain2AI.evaluate_word_topic(
            word=word.word, topic=word_list.title)
        if not result.isValid:
            raise HTTPException(
                status_code=400, detail=f"The new title {word_list.title} does not match the word {word.word} in the word list.")
    try:
        return crud.update_word_list(db=db, word_list=word_list)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error updating word list")


@router.delete("/", response_model=WordList)
async def delete_word_list(word_list_id: int, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    db_word_list = crud.get_word_list_by_id(
        db, word_list_id=word_list_id, user_id=user_id)

    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    try:
        return crud.delete_word_list(db=db, word_list_id=word_list_id)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error deleting word list")


@router.get("/get-all", response_model=List[WordList])
async def get_all_word_lists(db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    return crud.get_word_lists_by_uid(db=db, uid=user_id)


@router.get("/{word_list_id}", response_model=WordList)
async def get_word_list(word_list_id: int, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    db_word_list = crud.get_word_list_by_id(
        db, word_list_id=word_list_id, user_id=user_id)
    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")
    return db_word_list


@router.get("/{word_list_id}/more", response_model=WordList)
async def get_more_words(word_list_id: int, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    # Check if word_list_id exists
    db_word_list = crud.get_word_list_by_id(
        db, word_list_id=word_list_id, user_id=user_id)
    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    return crud.get_more_words(db=db, word_list_id=word_list_id)


@router.post("/words", response_model=WordList)
async def add_words(words: List[WordCreate], db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    # Check if user has access to the word list
    db_word_list = crud.get_word_list_by_id(
        db, word_list_id=words[0].wordListId, user_id=user_id)

    # Check if word list exists
    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    # Check if words are valid
    spelltrain2AI = SpellTrain2AI()
    for word in words:
        sanitized_word = re.sub(r'\s+', ' ', word.word).strip()
        result = spelltrain2AI.evaluate_word_topic(
            word=sanitized_word, topic=db_word_list.title)
        if not result.isValid:
            raise HTTPException(
                status_code=400, detail=f"{sanitized_word} is not a valid word.")

        # Check for repeat word in word list
        for db_word in db_word_list.words:
            if db_word.word.lower() == sanitized_word.lower():
                raise HTTPException(
                    status_code=400, detail=f"{word.word} already exists in the word list.")

    try:
        return crud.add_words(db=db, words=words)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error adding words")


@router.patch("/words", response_model=List[Word])
async def update_words(words: List[Word], db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    spelltrain2AI = SpellTrain2AI()

    for word in words:
        # Check if word list exists
        db_word_list = crud.get_word_list_by_id(
            db, word_list_id=word.wordListId, user_id=user_id)
        if db_word_list is None:
            raise HTTPException(
                status_code=404, detail=f"Word list not found")

        # Check if word exists
        db_word = crud.get_word_by_id(db, word_id=word.id)
        if db_word is None:
            raise HTTPException(
                status_code=404, detail=f"Word ID {word.id} not found")

        sanitized_word = re.sub(r'\s+', ' ', word.word).strip()

        # If the new word is different from the old word, check if the new word is valid and not a repeat word.
        if sanitized_word.lower() != db_word.word.lower():
            # Check for repeat word.
            for db_word in db_word_list.words:
                if db_word.word.lower() == sanitized_word.lower():
                    raise HTTPException(
                        status_code=400, detail=f"{word.word} already exists in the word list.")

            # Check if word is valid
            result = spelltrain2AI.evaluate_word_topic(
                word=sanitized_word, topic=db_word_list.title)
            if not result.isValid:
                raise HTTPException(
                    status_code=400, detail=f"{word.word} is not a valid word.")
    try:
        return crud.update_words(db=db, words_to_update=words)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error updating word")


@router.get("/words/{word_id}", response_model=Word)
async def get_word_info(word_id: int, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    db_word = crud.get_word_by_id(db, word_id=word_id)

    if db_word is None:
        raise HTTPException(
            status_code=404, detail=f"Word ID {word_id} not found")

    # Check if user has access to the word list
    db_word_list = crud.get_word_list_by_id(
        db, word_list_id=db_word.wordListId, user_id=user_id)

    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    # Check if definition, rootOrigin, usage, languageOrigin, partsOfSpeech, alternatePronunciation are empty
    if db_word.definition == '' or db_word.rootOrigin == '' or db_word.usage == '' or db_word.languageOrigin == '' or db_word.partsOfSpeech == '' or db_word.alternatePronunciation == '':
        try:
            word_info = crud.get_word_info(db=db, word_id=word_id)

            return word_info
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=400, detail="Error retrieving word info")

    return db_word


@router.delete("/words", response_model=List[Word])
async def delete_words(
    word_ids: List[int] = Query(...,
                                description="List of word IDs to delete", min_items=1),
    db: Session = Depends(get_db),
    user_id=Depends(RequiredLogin())
):

    for word_id in word_ids:
        # Check if user has access to the word list
        db_word = crud.get_word_by_id(db, word_id=word_id)
        if db_word is None:
            raise HTTPException(
                status_code=404, detail=f"Word ID {word_id} not found")

        db_word_list = crud.get_word_list_by_id(
            db, word_list_id=db_word.wordListId, user_id=user_id)
        if db_word_list is None:
            raise HTTPException(
                status_code=404, detail=f"Word list not found")

    # If all word IDs exist, delete them
    try:
        return crud.delete_words(db=db, word_ids=word_ids)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error deleting word"
        )
