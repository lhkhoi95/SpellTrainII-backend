from api.database import get_db_session
from api.crud.word_lists import get_all_words
from api.utils.helpers import delete_audio_file
import os


def delete_orphaned_audio_files():
    print("\033[92m" + "Deleting orphaned audio files..." + "\033[0m")
    SessionLocal, _ = get_db_session()
    db = SessionLocal()

    try:
        # Get all audio URLs from the database
        db_audio_urls = [word.audioUrl.replace(
            "audio/", "") for word in get_all_words(db)]

        # Get all audio filenames from the audio directory
        audio_dir_filenames = os.listdir("audio/")

        # Find orphaned audio files
        orphaned_audio_files = [
            filename for filename in audio_dir_filenames
            if filename not in db_audio_urls
        ]

        # Delete orphaned audio files
        for filename in orphaned_audio_files:
            delete_audio_file(f"audio/{filename}")
    finally:
        db.close()
