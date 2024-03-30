from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.models import models
from api.schemas import schemas


def find_game_by_word_list_id(db: Session, word_list_id: int):
    return db.query(models.Game).filter(models.Game.wordListId == word_list_id).first()


def find_stations_by_game_id(db: Session, game_id: int):
    return db.query(models.Station).filter(models.Station.gameId == game_id).all()


def create_game_and_stations(db: Session, game: schemas.GameCreate, stations: List[schemas.StationCreate]):
    try:
        # Create game
        db_game = models.Game(**game.model_dump())
        db.add(db_game)
        db.flush()  # Flush to get the id of the game

        # Create each station with the game id
        db_stations = []
        for station in stations:
            station_dict = station.model_dump()
            station_dict.update({"gameId": db_game.id})
            db_station = models.Station(**station_dict)
            db.add(db_station)
            db_stations.append(db_station)

        db.commit()

        # Refresh the game and each station
        db.refresh(db_game)
        for db_station in db_stations:
            db.refresh(db_station)

        return db_stations
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=400, detail="Failed to create game and stations in the database.")
