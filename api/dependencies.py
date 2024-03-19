import os
from fastapi import HTTPException, Request
from openai import OpenAI, OpenAIError
import google.generativeai as genai


def get_db(request: Request):
    return request.state.db


def openai_client():
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        return client
    except OpenAIError:
        raise HTTPException(
            status_code=500, detail="Error configuring OpenAI API Key")


def google_gemini_client(model='gemini-pro'):
    try:
        genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
        gemini = genai.GenerativeModel(model)

        return gemini
    except Exception:
        raise HTTPException(
            status_code=500, detail="Error configuring Google Gemini API Key")


def check_env():
    env_vars = [
        "SPELLTRAIN2_DATABASE_URL",
        "OPENAI_API_KEY",
        "GOOGLE_GEMINI_API_KEY",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",

    ]
    if os.getenv("TEST_MODE") == "True":
        print("\033[92m" + "Running in test mode." + "\033[0m")

    for env_var in env_vars:
        if not os.getenv(env_var):
            raise HTTPException(
                status_code=500, detail="\033[91m" + "Environment variable: " + env_var + " is not set." + "\033[0m")
    print("\033[92m" + "All environment variables are set." + "\033[0m")
