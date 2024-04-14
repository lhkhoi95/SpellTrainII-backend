import os
from fastapi import Depends
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.auth.auth_bearer import RequiredLogin
from api.crud import users as crud
from api.schemas import schemas
from api.dependencies import get_db
from api.auth.auth_handler import *

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


@router.post("/login", response_model=schemas.UserLoginResponse)
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db=db, user=user)
    if not authenticated_user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_user = crud.get_user_by_email(db=db, email=user.email)
    access_token_expires = timedelta(minutes=int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )

    return {
        "name": db_user.name,
        "email": db_user.email,
        "phone": db_user.phone,
        "wordLists": db_user.wordLists,
        "accessToken": access_token
    }


@router.get("/protected")
async def protected_route_test(user_id=Depends(RequiredLogin())) -> dict:
    print(user_id)
    return {
        "data": user_id
    }


@router.get("/", response_model=schemas.UserResponse)
async def get_user(db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/", response_model=schemas.UserResponse)
async def update_user(user: schemas.UserUpdate, db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=db_user.id, user=user)


@router.delete("/", response_model=schemas.UserResponse)
async def delete_user(db: Session = Depends(get_db), user_id=Depends(RequiredLogin())):
    if user_id:
        db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.delete_user(db=db, user_id=db_user.id)


# @router.get("/email/{email}", response_model=schemas.UserResponse)
# async def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)):
#     """
#     Retrieve a user by their email.

#     Args:
#         email (EmailStr): The email of the user to retrieve.
#         db (Session, optional): The database session. Defaults to Depends(get_db).

#     Returns:
#         schemas.User: The user object.

#     Raises:
#         HTTPException: If the user is not found.
#     """
#     db_user = crud.get_user_by_email(db, email=email)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


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
