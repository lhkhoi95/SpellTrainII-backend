import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.auth.auth_bearer import RequiredLogin
from api.crud.word_lists import get_word_info, get_word_list_by_id
from api.schemas.schemas import GameCreate, StationCreate
from api.utils.game import Game
from api.crud import games as games_crud
import json


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.post("/")
async def retrieve_games(word_list_id: int, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    word_list_db = get_word_list_by_id(db, word_list_id, user_id)

    if not word_list_db:
        raise HTTPException(
            status_code=400, detail="Word list not found")

    if len(word_list_db.words) < 6:
        raise HTTPException(
            status_code=400, detail="Please provide at least 6 words to generate games.")

    game_db = games_crud.find_game_by_word_list_id(
        db=db, word_list_id=word_list_db.id)

    # Return the game progress if the game exists
    if game_db:
        return games_crud.find_stations_by_game_id(db, game_db.id)

    # Create a new game if the game does not exist
    start, end, station_number = 0, 6, 1

    # Select words from the range of indices
    words = word_list_db.words[start:end]

    db_words = []
    for word in words:
        # If any of the fields are empty, fetch the word from the database
        if word.languageOrigin == "" or word.usage == "" or word.alternatePronunciation == "" or word.definition == "":
            db_words.append(get_word_info(db, word.id))
        else:
            db_words.append(word)

    game_object = Game(words=db_words)
    game_bank = game_object.generate_games()

    # Create a new game model
    game_model = GameCreate(
        wordListId=word_list_id,
        startingIndex=start,
        endingIndex=end
    )

    # Create 8 station models
    stations_models = []
    for level, games in game_bank.items():
        station_to_save = StationCreate(
            stationNumber=station_number,
            level=level.replace("level", ""),
            games=json.dumps(games)
        )
        stations_models.append(station_to_save)

    return games_crud.create_game_and_stations(db, game_model, stations_models)
