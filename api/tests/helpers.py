from api.schemas import schemas

USER_EMAIL = "test@gmail.com"
UPDATED_EMAIL = "test_updated@gmail.com"

INVALID_INT_IDS = [-999, 999]
INVALID_IDS = [-999, "abc", "123", "xyz",
               "abc123", "123abc", "abcxyz", "xyzabc"]

TEST_USER = schemas.UserCreate(
    name="Test User",
    email=USER_EMAIL,
    phone="1234567890",
    wordLists=[],
    password="testpassword")

UPDATED_TEST_USER = {
    "email": UPDATED_EMAIL,
    "isActive": False,
    "name": "New Name",
    "password": "newpassword",
    "phone": "1234567890"
}

TOPIC1 = "Science"
TOPIC2 = "Technology"

TECH_WORDS = [
    "Hardware",
    "Software",
    "Computer",
    "Machine Learning",
]

TECH_WORDS_WITH_SPACES = [
    "Machine Learning      ",
    "Machine        Learning",
    "      Machine Learning",
]

INVALID_TOPICS = [
    "Unknown",
    "Killing",
    "Drug Abuse",
    "xyz",
]

INVALID_WORD = [
    {
        "id": -999,  # invalid id
        "word": "string",
        "definition": "string",
        "rootOrigin": "string",
        "usage": "string",
        "languageOrigin": "string",
        "partsOfSpeech": "string",
        "alternatePronunciation": "string",
        "wordListId": 1
    }
]

INVALID_WORD_LIST_ID = [
    {
        "id": 1,
        "word": "string",
        "definition": "string",
        "rootOrigin": "string",
        "usage": "string",
        "languageOrigin": "string",
        "partsOfSpeech": "string",
        "alternatePronunciation": "string",
        "wordListId": -999  # invalid id
    }
]

INVALID_WORD_LISTS_TO_UPDATE = [
    {
        "id": -999,
        "title": "Test update title"
    },
    {
        "id": 999,
        "title": "Test update title"
    }
]

IRRELEVANT_WORDS = [
    "Tree", "Book", "Flower", "Sunset", "Rainbow", "123", "abc", "xyz", "abc123", "123abc", "abcxyz", "xyzabc", 123, 999, -999
]
