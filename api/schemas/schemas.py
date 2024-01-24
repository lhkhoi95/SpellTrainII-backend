from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class Word(BaseModel):
    id: int
    word: str
    definition: Optional[str] = None
    rootOrigin: Optional[str] = None
    usage: Optional[str] = None
    languageOrigin: Optional[str] = None
    partsOfSpeech: Optional[str] = None
    alternatePronunciation: Optional[str] = None
    wordListId: int

    # This allows us to convert any kind of objects to Pydantic models
    model_config = ConfigDict(from_attributes=True)


class WordCreate(BaseModel):
    word: str
    wordListId: int

    # This allows us to convert any kind of objects to Pydantic models
    model_config = ConfigDict(from_attributes=True)


class WordInfo(BaseModel):
    definition: str
    rootOrigin: str
    usage: str
    languageOrigin: str
    partsOfSpeech: str
    alternatePronunciation: str

    # This allows us to convert any kind of objects to Pydantic models
    model_config = ConfigDict(from_attributes=True)


class WordList(BaseModel):
    id: int
    title: str
    ownerId: int
    words: List[Word] = []


class WordListUpdate(BaseModel):
    id: int
    title: str


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    wordLists: List[WordList] = []


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    isActive: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Charlie",
                    "email": "charlie@gmail.com",
                    "phone": "1234567890",
                    "password": "newpassword",
                    "isActive": True
                }
            ]
        }
    }

    # class Config:
    # this will raise an error if there are extra fields in the request body
    #     extra = 'forbid'


class UserResponse(UserBase):
    id: str | int
    isActive: bool


class EvaluatedInput(BaseModel):
    isValid: bool


class EvaluatedTopic(EvaluatedInput):
    reason: str

    # This allows us to convert any kind of objects to Pydantic models
    model_config = ConfigDict(from_attributes=True)
