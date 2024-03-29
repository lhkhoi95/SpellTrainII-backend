from sqlalchemy.orm import Session
from api.models import models
from api.schemas import schemas
from api import crud


def save_game_progress(db: Session, game: schemas.Game):
    # Find the game in the database
    db_game = db.query(models.Game).filter(
        models.Game.wordListId == game.wordListId).first()

    # If the game does not exist, create a new game
    if not db_game:
        db_game = models.Game(**game.model_dump())
        db.add(db_game)
    else:
        # Update the game
        fields_to_update = game.model_dump(exclude_unset=True)
        for key, value in fields_to_update.items():
            setattr(db_game, key, value)

    db.commit()
    db.refresh(db_game)
    return db_game


def find_game_by_word_list_id(db: Session, word_list_id: int):
    return db.query(models.Game).filter(models.Game.wordListId == word_list_id).first()
