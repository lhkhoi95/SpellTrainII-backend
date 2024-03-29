import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.auth.auth_bearer import RequiredLogin
from api.crud.word_lists import get_word_info, get_word_list_by_id
from api.schemas.schemas import GameCreate
from api.utils.game import Game
from api.crud import games as games_crud
import json


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get("/")
async def generate_games(word_list_id: int, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    word_list_db = get_word_list_by_id(db, word_list_id, user_id)

    if not word_list_db:
        raise HTTPException(
            status_code=400, detail="Word list not found")

    if len(word_list_db.words) < 6:
        raise HTTPException(
            status_code=400, detail="Word list must have at least 6 words")

    game_db = games_crud.find_game_by_word_list_id(
        db=db, word_list_id=word_list_db.id)
    if not game_db:
        start, end, level = 0, 6, 1
    else:
        start, end, level = game_db.startingIndex, game_db.endingIndex, game_db.level
        if end + 1 >= len(word_list_db.words):
            raise HTTPException(
                status_code=400, detail="No more games to generate")
        start += 1
        end += 1

    # Select words from the range of indices
    words = word_list_db.words[start:end]

    db_words = []
    for word in words:
        # If any of the fields are empty, fetch the word from the database
        if word.languageOrigin == "" or word.usage == "" or word.alternatePronunciation == "":
            db_words.append(get_word_info(db, word.id))
        else:
            db_words.append(word)

    game = Game(words=db_words, level=level)
    games_bank = game.generate_games()

    game_model = GameCreate(
        level=1,
        games_bank=json.dumps(games_bank),
        startingIndex=start,
        endingIndex=end,
        wordListId=word_list_db.id,
    )

    # Store the game in the database
    return games_crud.save_game_progress(db, game_model)
