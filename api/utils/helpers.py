import os
from typing import List
from gtts import gTTS
import uuid


def word_dict(word: str):
    return {
        "word": word,
        "definition": "",
        "rootOrigin": "",
        "usage": "",
        "languageOrigin": "",
        "partsOfSpeech": "",
        "alternatePronunciation": "",
        "audioUrl": "",
    }


def get_audio_url(word: str):
    # Create a speech object
    tts = gTTS(text=word, lang='en')
    # Generate a unique id for the file name
    unique_id = str(uuid.uuid4())
    # Save the audio file
    audio_file = f"audio/word_{unique_id}.mp3"
    tts.save(audio_file)

    return audio_file


def delete_audio_file(audio_url: str | List[str]):
    if isinstance(audio_url, list):
        for url in audio_url:
            os.remove(url)
    else:
        os.remove(audio_url)
