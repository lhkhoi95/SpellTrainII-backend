from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.models import models
from api.schemas import schemas


def find_game_by_word_list_id(db: Session, word_list_id: int):
    return db.query(models.Game).filter(models.Game.wordListId == word_list_id).first()


def find_game_by_id(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.id == game_id).first()


def find_stations_by_game_id(db: Session, game_id: int):
    return db.query(models.Station).filter(models.Station.gameId == game_id).all()


def find_last_station_by_game_id(db: Session, game_id: int):
    return db.query(models.Station).filter(models.Station.gameId == game_id).order_by(models.Station.id.desc()).first()


def find_owner_by_game_id(db: Session, game_id: int):
    return db.query(models.User).join(models.WordList).join(models.Game).filter(models.Game.id == game_id).first()


def find_station_by_id(db: Session, station_id: int):
    return db.query(models.Station).filter(models.Station.id == station_id).first()


def check_route_completion(db: Session, game_id: int, route: int):
    uncompleted_levels = []
    stations = db.query(models.Station).filter(
        models.Station.gameId == game_id, models.Station.route == route).all()
    # Check if level 1 to level 8 are completed.
    for station in stations:
        if not station.isCompleted:
            uncompleted_levels.append(station)
    return uncompleted_levels


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


def update_game_and_stations(db: Session, game_id: int, stations: List[schemas.StationCreate]):
    try:
        # Find game
        db_game = db.query(models.Game).filter(
            models.Game.id == game_id).first()

        # Increment the ending index by 6
        db_game.endingIndex += 6
        db.add(db_game)
        db.flush()

        # Add new stations to the database.
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
            status_code=400, detail="Failed to update game and stations in the database.")


def mark_station_as_completed(db: Session, station_id: int):
    db_station = db.query(models.Station).filter(
        models.Station.id == station_id).first()

    db_station.isCompleted = True
    db.commit()
    db.refresh(db_station)

    return db_station
