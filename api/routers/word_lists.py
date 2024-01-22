from turtle import update
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from api.crud import word_lists as crud
from api.dependencies import get_db
from api.schemas.schemas import WordList, Word, WordListUpdate
from api.utils.SpellTrainII_AI import SpellTrain2AI

router = APIRouter(
    prefix="/word-lists",
    tags=["word-lists"],
)


@router.get("/", response_model=WordList)
async def create_generative_word_list(topic: str, db: Session = Depends(get_db)):
    """
    Create a generative word list for the given topic.

    Parameters:
    - topic (str): The topic for which the word list is to be created.
    - db (Session): The database session.

    Returns:
    - WordList: The created generative word list.

    Raises:
    - HTTPException: If the topic is invalid.
    """
    user_id = 1  # TODO: get user id from auth token. This route requires user login
    spelltrain2AI = SpellTrain2AI()

    # Validate topic
    evaluated_topic = spelltrain2AI.evaluate_topic(topic)
    # If topic is invalid, raise an exception with the reason
    if not evaluated_topic.isValid:
        raise HTTPException(
            status_code=400, detail=evaluated_topic.reason)

    # Check if title already exists
    db_word_list = crud.get_word_list_by_title(db=db, title=topic)

    # If title exists, return the list
    if db_word_list:
        return db_word_list

    return crud.create_generative_word_list(db=db, topic=topic, user_id=user_id)


@router.patch("/", response_model=WordList)
async def update_word_list(word_list: WordListUpdate, db: Session = Depends(get_db)):
    """
    Update a word list in the database.

    Parameters:
    - word_list: The updated WordList object.
    - db: The database session.

    Returns:
    The updated WordList object.

    Raises:
    - HTTPException(404): If the word list is not found.
    - HTTPException(400): If there is an error updating the word list.
    """
    # Check if word_list_id exists
    db_word_list = crud.get_word_list_by_id(db, word_list_id=word_list.id)

    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    # TODO: Check if word list belongs to user

    try:
        return crud.update_word_list(db=db, word_list=word_list)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error updating word list")


@router.delete("/", response_model=WordList)
async def delete_word_list(word_list_id: int, db: Session = Depends(get_db)):
    """
    Delete a word list by its ID.

    Parameters:
    - word_list_id (int): The ID of the word list to be deleted.
    - db (Session): The database session.

    Returns:
    - WordList: The deleted word list.

    Raises:
    - HTTPException: If the word list is not found or there is an error deleting it.
    """
    db_word_list = crud.get_word_list_by_id(db, word_list_id=word_list_id)

    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    # TODO: Check if word list belongs to user

    try:
        return crud.delete_word_list(db=db, word_list_id=word_list_id)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error deleting word list")


@router.get("/get-all", response_model=List[WordList])
async def get_all_word_lists(db: Session = Depends(get_db)):
    """
    Retrieve all word lists associated with a user ID.

    Parameters:
    - db (Session): The database session.

    Returns:
    - List[WordList]: A list of WordList objects associated with the user ID.
    """
    # dummy user id
    user_id = 1  # TODO: get user id from auth token. This route requires user login
    return crud.get_word_lists_by_uid(db=db, uid=user_id)


@router.get("/{word_list_id}", response_model=WordList)
async def get_word_list(word_list_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a word list by its ID.

    Args:
        word_list_id (int): The ID of the word list to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        WordList: The retrieved word list.

    Raises:
        HTTPException: If the word list is not found.
    """
    db_word_list = crud.get_word_list_by_id(db, word_list_id=word_list_id)
    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")
    return db_word_list


@router.get("/{word_list_id}/more", response_model=WordList)
async def get_more_words(word_list_id: int, db: Session = Depends(get_db)):
    """
    Retrieve additional words from a word list.

    Args:
        word_list_id (int): The ID of the word list.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        WordList: The word list with additional words.

    Raises:
        HTTPException: If the word list with the given ID is not found.
    """
    # Check if word_list_id exists
    db_word_list = crud.get_word_list_by_id(db, word_list_id=word_list_id)
    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    return crud.get_more_words(db=db, word_list_id=word_list_id)


@router.patch("/words", response_model=List[Word])
async def update_words(words: List[Word], db: Session = Depends(get_db)):
    """
    Update a list of words in the database.

    Args:
        words (List[Word]): The list of words to be updated.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[Word]: The updated list of words.
    """
    updated_words: List[Word] = []

    for word in words:

        # Check if word exists
        db_word = crud.get_word_by_id(db, word_id=word.id)
        if db_word is None:
            raise HTTPException(status_code=404, detail="Word not found")

        # TODO: Check if word belongs to user

        # Check if the word belongs to the word list
        if db_word.wordListId != word.wordListId:
            raise HTTPException(
                status_code=400, detail="Word does not belong to the word list")

        try:
            updated_word = crud.update_word(db=db, word=word)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=400, detail="Error updating word")

        updated_words.append(updated_word)

    return updated_words


@router.get("/words/{word_id}", response_model=Word)
async def get_word_info(word_id: int, db: Session = Depends(get_db)):
    """
    Retrieve information about a word by its ID.

    Args:
        word_id (int): The ID of the word.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Union[Word, Dict[str, Any]]: The word information if found, otherwise raises an HTTPException.

    Raises:
        HTTPException: If the word is not found or there is an error retrieving the word info.
    """
    db_word = crud.get_word_by_id(db, word_id=word_id)
    if db_word is None:
        raise HTTPException(status_code=404, detail="Word not found")

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
    db: Session = Depends(get_db)
):
    """
    Delete multiple words from the database.

    Args:
        word_ids (List[int]): List of word IDs to delete.
        db (Session): Database session.

    Returns:
        List[Word]: List of deleted words.

    Raises:
        HTTPException: If any of the word IDs are not found or there is an error deleting the word.
    """
    # Check if all word IDs exist
    for word_id in word_ids:
        db_word = crud.get_word_by_id(db, word_id=word_id)
        if db_word is None:
            raise HTTPException(
                status_code=404, detail=f"Word id {word_id} not found"
            )

    # If all word IDs exist, delete them
    try:
        return crud.delete_words(db=db, word_ids=word_ids)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error deleting word"
        )
