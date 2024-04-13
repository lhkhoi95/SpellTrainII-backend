from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, Json


class StationBase(BaseModel):
    level: int
    games: Json[Any]
    route: int
    isCompleted: bool = False
    gameId: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class StationCreate(StationBase):
    pass


class Station(StationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class GameBase(BaseModel):
    wordListId: int
    endingIndex: int


class GameCreate(GameBase):
    pass


class Game(GameBase):
    id: int
    stations: List[Station] = []

    model_config = ConfigDict(from_attributes=True)


class Word(BaseModel):
    id: int
    word: str = Field(..., max_length=50, min_length=1)
    definition: Optional[str] = None
    rootOrigin: Optional[str] = None
    usage: Optional[str] = None
    languageOrigin: Optional[str] = None
    partsOfSpeech: Optional[str] = None
    alternatePronunciation: Optional[str] = None
    audioUrl: Optional[str] = None
    isAIGenerated: bool = Field(default=True)
    wordListId: int

    # This allows us to convert any kind of objects to Pydantic models
    model_config = ConfigDict(from_attributes=True)


class CustomWord(BaseModel):
    word: str = Field(..., max_length=50, min_length=1)
    definition: str = Field(..., max_length=50)
    rootOrigin: str = Field(..., max_length=50)
    usage: str = Field(..., max_length=100)
    languageOrigin: str = Field(..., max_length=50)
    partsOfSpeech: str = Field(..., max_length=50)
    alternatePronunciation: str = Field(..., max_length=50)
    audioUrl: Optional[str] = ""

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
    title: str = Field(..., min_length=2)
    ownerId: int
    isAIGenerated: Optional[bool] = True
    words: List[Word] = []


class CustomWordList(BaseModel):
    title: str = Field(min_length=2)
    words: List[CustomWord] = Field(max_length=30)


class WordListUpdate(BaseModel):
    id: int
    title: str = Field(min_length=2)


class UserBase(BaseModel):
    name: str | None = None
    email: EmailStr
    phone: str | None = None
    wordLists: List[WordList] | None = []
    # This allows us to convert any kind of objects to Pydantic models
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLoginResponse(UserBase):
    accessToken: str

    # This allows us to convert any kind of objects to Pydantic models
    model_config = ConfigDict(from_attributes=True)


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
