from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from api.dependencies import get_db
from api.auth.auth_bearer import RequiredLogin
from api.crud.word_lists import get_word_info, get_word_list_by_id, get_more_words
from api.schemas.schemas import GameCreate, StationCreate
from api.utils.game import Game
from api.crud import games as games_crud
from api.database import get_db_session
import json


router = APIRouter(
    prefix="/games",
    tags=["games"],
)

LEVEL_MAX = 8
MAX_ROUTES_ALLOWED = 5
WORDS_PER_ROUTE = 6


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
    end, route = 6, 1

    # Select words from the range of indices
    words = word_list_db.words[:end]

    db_words = []
    for word in words:
        # If any of the fields are empty, fetch the word from the database
        if word.languageOrigin == "" or word.usage == "" or word.definition == "":
            db_words.append(get_word_info(db, word.id))
        else:
            db_words.append(word)

    game_object = Game(words=db_words)
    game_bank = game_object.generate_games()

    # Create a new game model
    game_model = GameCreate(
        wordListId=word_list_id,
        endingIndex=end
    )

    # Create 8 station models
    stations_models = []
    for level, games in game_bank.items():
        station_to_save = StationCreate(
            route=route,
            level=level.replace("level", ""),
            games=json.dumps(games)
        )
        stations_models.append(station_to_save)

    return games_crud.create_game_and_stations(db, game_model, stations_models)


@router.patch("/stations/{station_id}")
async def mark_station_as_completed(station_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    station_db = games_crud.find_station_by_id(db, station_id)

    if not station_db:
        raise HTTPException(
            status_code=400, detail="Station not found")

    # Check if user is the owner of the game
    owner = games_crud.find_owner_by_game_id(db, station_db.gameId)
    if int(owner.id) != int(user_id):
        raise HTTPException(
            status_code=401, detail="Unauthorized access")

    # Run the background task to prepare the next route
    background_tasks.add_task(prepare_next_route, station_db, user_id,)

    return games_crud.mark_station_as_completed(db, station_id)


@router.post("/next-route")
async def retrieve_games_for_next_route(game_id: int, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    game_db = games_crud.find_game_by_id(db, game_id)

    if not game_db:
        raise HTTPException(
            status_code=400, detail="Game not found")

    # Check if the user is the owner of the game
    owner = games_crud.find_owner_by_game_id(db, game_id)

    if int(owner.id) != int(user_id):
        raise HTTPException(
            status_code=401, detail="Unauthorized access")

    # Get the last station of the game
    last_station = games_crud.find_last_station_by_game_id(db, game_id)
    route = last_station.route

    # Check if user has completed the current route.
    uncompleted_stations = games_crud.check_route_completion(
        db, game_id, route)
    if len(uncompleted_stations) > 0:
        uncompleted_levels = [
            station.level for station in uncompleted_stations]
        uncompleted_station_ids = [
            station.id for station in uncompleted_stations]
        raise HTTPException(
            status_code=400, detail={
                "uncompleted_station_ids": uncompleted_station_ids,
                "message": f"Please complete levels {uncompleted_levels} of route {route} to proceed to the next route."})

    # If the user completed all the routes, return congratulations message.
    if last_station.route >= MAX_ROUTES_ALLOWED:
        return {"message": "Congratulations! You have completed all the challenges for this word list."}

    # Get the next 6 words for the next route
    start, end = game_db.endingIndex, game_db.endingIndex + WORDS_PER_ROUTE
    next_route = route + 1

    # Select words from the range of indices
    word_list_db = get_word_list_by_id(db, game_db.wordListId, user_id)

    if not word_list_db:
        raise HTTPException(
            status_code=400, detail="Word list not found")
    words = word_list_db.words[start:end]

    db_words = []
    for word in words:
        # If any of the fields are empty, fetch the word from the database
        if word.languageOrigin == "" or word.usage == "" or word.definition == "":
            db_words.append(get_word_info(db, word.id))
        else:
            db_words.append(word)

    game_object = Game(words=db_words)
    game_bank = game_object.generate_games()

    # Create 8 station models
    stations_models = []
    for level, games in game_bank.items():
        station_to_save = StationCreate(
            route=next_route,
            level=level.replace("level", ""),
            games=json.dumps(games)
        )
        stations_models.append(station_to_save)

    # Return the updated game and stations for the next route
    return games_crud.update_game_and_stations(
        db=db, game_id=game_db.id, stations=stations_models)


def prepare_next_route(station_db, user_id):
    try:
        SessionLocal, _ = get_db_session()
        db = SessionLocal()
        if station_db.route < MAX_ROUTES_ALLOWED:
            game_db = games_crud.find_game_by_id(db, station_db.gameId)
            index = game_db.endingIndex + station_db.level - 1
            word_list_db = get_word_list_by_id(db, game_db.wordListId, user_id)

            # If no more words are available, fetch more words
            if index >= len(word_list_db.words):
                word_list_db = get_more_words(
                    db=db, word_list_id=game_db.wordListId)

            if not word_list_db:
                print("Failed to fetch more words")
                return

            word = word_list_db.words[index]

            # Fetch the word information if not already fetched.
            if word.languageOrigin == "" or word.usage == "" or word.definition == "":
                fetch_word = get_word_info(db, word.id)
                if not fetch_word:
                    print("Failed to fetch word information")
                    return
    except Exception as e:
        print(f"Failed to prepare next route: {e}")
