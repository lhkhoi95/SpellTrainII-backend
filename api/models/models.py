from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import uuid

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
    ownerId = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="wordLists")
    words = relationship(
        "Word",
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

    wordListId = Column(
        Integer,
        ForeignKey('word_lists.id', ondelete="CASCADE"))
    wordList = relationship("WordList", back_populates="words")
