import os
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


def get_db_session():
    if os.getenv("TEST_MODE") == "True":
        SQLALCHEMY_DATABASE_URL = os.getenv(
            "SPELLTRAIN2_DATABASE_URL_TEST", "sqlite:///./test.db")
    else:
        SQLALCHEMY_DATABASE_URL = os.getenv(
            "SPELLTRAIN2_DATABASE_URL", "sqlite:///./api/spelltrain2.db")

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal, engine
