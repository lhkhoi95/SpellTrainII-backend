from dotenv import load_dotenv
import os

load_dotenv(".env.test")  # load environment variables from .env.test file
os.environ["TEST_MODE"] = "True"  # set TEST_MODE environment variable to True
