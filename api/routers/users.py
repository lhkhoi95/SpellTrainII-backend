from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from api.crud import users as crud
from api.schemas import schemas
from api.dependencies import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    The id field is optional. If not provided, it will be auto-generated.

    Args:
        user (schemas.UserCreate): The user data to be created.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        schemas.User: The created user object.
    """
    db_user = crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(
            status_code=400, detail="Email already registered")

    return crud.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a user by their ID.

    Args:
        user_id: (str): The ID of the user to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        schemas.User: The user object.

    Raises:
        HTTPException: If the user is not found.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/", response_model=schemas.UserResponse)
async def update_user(user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user in the database.

    Note*: Only pass in the fields that need to be updated.

    Args:
        user (schemas.UserUpdate): The updated user data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        schemas.UserResponse: The updated user data.

    Raises:
        HTTPException: If the user is not found in the database.
    """
    user_id = 1  # TODO: get user id from token

    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=user_id, user=user)


@router.delete("/", response_model=schemas.UserResponse)
async def delete_user(user_id: str = None, user_email: EmailStr = None, db: Session = Depends(get_db)):
    """
    Delete a user.

    Args:
        user_id: (str, optional): The ID of the user to delete.
        user_email (EmailStr, optional): The email of the user to delete.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        schemas.User: The deleted user object.

    Raises:
        HTTPException: If the user is not found.
    """
    if user_id is None and user_email is None:
        raise HTTPException(
            status_code=400, detail="Either user_id or user_email must be provided")

    if user_id:
        db_user = crud.get_user(db, user_id=user_id)
    else:
        db_user = crud.get_user_by_email(db, email=user_email)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.delete_user(db=db, user_id=db_user.id)


@router.get("/email/{email}", response_model=schemas.UserResponse)
async def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)):
    """
    Retrieve a user by their email.

    Args:
        email (EmailStr): The email of the user to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        schemas.User: The user object.

    Raises:
        HTTPException: If the user is not found.
    """
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# @router.patch("/activate", response_model=schemas.UserResponse)
# async def set_active(user_id: str = None, user_email: EmailStr = None, db: Session = Depends(get_db)):
#     """
#     Activate a user.

#     Args:
#         user_id: (str, optional): The ID of the user to activate.
#         user_email (EmailStr, optional): The email of the user to activate.
#         db (Session, optional): The database session. Defaults to Depends(get_db).

#     Returns:
#         schemas.User: The activated user object.

#     Raises:
#         HTTPException: If the user is not found.
#     """
#     if user_id is None and user_email is None:
#         raise HTTPException(
#             status_code=400, detail="Either user_id or user_email must be provided")

#     if user_id:
#         db_user = crud.get_user(db, user_id=user_id)
#     else:
#         db_user = crud.get_user_by_email(db, email=user_email)

#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     return crud.set_active(db=db, user_id=db_user.id)


# @router.patch("/deactivate", response_model=schemas.UserResponse)
# async def set_inactive(user_id: str = None, user_email: EmailStr = None, db: Session = Depends(get_db)):
#     """
#     Deactivate a user.

#     Args:
#         user_id: (str, optional): The ID of the user to deactivate.
#         user_email (EmailStr, optional): The email of the user to deactivate.
#         db (Session, optional): The database session. Defaults to Depends(get_db).

#     Returns:
#         schemas.User: The deactivated user object.

#     Raises:
#         HTTPException: If the user is not found.
#     """
#     if user_id is None and user_email is None:
#         raise HTTPException(
#             status_code=400, detail="Either user_id or user_email must be provided")

#     if user_id:
#         db_user = crud.get_user(db, user_id=user_id)
#     else:
#         db_user = crud.get_user_by_email(db, email=user_email)

#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     return crud.set_inactive(db=db, user_id=db_user.id)
