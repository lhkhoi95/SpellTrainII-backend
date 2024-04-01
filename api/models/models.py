from sqlalchemy import JSON, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    # id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    phone = Column(String)
    email = Column(String)
    isActive = Column(Boolean, default=True)

    wordLists = relationship(
        "WordList", back_populates="owner", cascade="all, delete-orphan")


class WordList(Base):
    __tablename__ = 'word_lists'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    isAIGenerated = Column(Boolean, default=True)
    ownerId = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="wordLists")
    words = relationship(
        "Word",
        cascade="all, delete-orphan",
        back_populates="wordList")
    games = relationship(
        "Game",
        cascade="all, delete-orphan",
        back_populates="wordList")


class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    word = Column(String)
    definition = Column(String)
    rootOrigin = Column(String)
    usage = Column(String)
    languageOrigin = Column(String)
    partsOfSpeech = Column(String)
    alternatePronunciation = Column(String)
    audioUrl = Column(String)
    isAIGenerated = Column(Boolean, default=True)

    wordListId = Column(
        Integer,
        ForeignKey('word_lists.id', ondelete="CASCADE"))
    wordList = relationship("WordList", back_populates="words")


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    endingIndex = Column(Integer, default=0)

    wordListId = Column(
        Integer,
        ForeignKey('word_lists.id', ondelete="CASCADE"))
    wordList = relationship("WordList", back_populates="games")
    stations = relationship(
        "Station",
        cascade="all, delete-orphan",
        back_populates="game")


class Station(Base):
    __tablename__ = 'stations'

    id = Column(Integer, primary_key=True)
    route = Column(Integer)
    level = Column(Integer, default=1)
    isCompleted = Column(Boolean, default=False)
    games = Column(JSON)

    gameId = Column(
        Integer,
        ForeignKey('games.id', ondelete="CASCADE"))
    game = relationship("Game", back_populates="stations")
