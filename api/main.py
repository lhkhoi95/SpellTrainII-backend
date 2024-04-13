from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

from api.routers import games
from api.utils import delete_orphaned_audio_files
from .models import models
from .database import get_db_session
from .routers import users, word_lists
from .dependencies import check_env
import os

load_dotenv()
check_env()
# Create database tables
SessionLocal, engine = get_db_session()
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
# Create audio directory if it doesn't exist
if not os.path.exists("audio"):
    os.makedirs("audio")
app.mount("/audio", StaticFiles(directory="audio"), name="audio")
app.include_router(users.router)
app.include_router(word_lists.router)
app.include_router(games.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    delete_orphaned_audio_files.delete_orphaned_audio_files()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.get("/")
async def greeting():
    return {"message": "SpellTrain II API"}
