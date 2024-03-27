USER_EMAIL = "test@gmail.com"
USER_EMAIL_2 = "test2@gmail.com"
UPDATED_EMAIL = "test_updated@gmail.com"
CUSTOM_WORD_LIST_TITLE = "Computer"
CUSTOM_WORDS = ['Ram', 'CPU', 'GPU', 'Mother Board']
INVALID_INT_IDS = [-999, 0, 999]
INVALID_STR_IDS = ['abc', '123', 'abc123', '123abc', 'abc123xyz', '123abcxyz']
INVALID_TITLE_LENGTH_MSG = "String should have at least 2 characters"
INVALID_WORD_LENGTH_MSG = "String should have at least 1 character"

TEST_USER = {
    'name': 'Test User',
    'email': USER_EMAIL,
    'phone': '1234567890',
    'wordLists': [],
    'password': 'testpassword'
}

TEST_USER_RESPONSE = {
    'name': 'Test User',
    'email': USER_EMAIL,
    'phone': '1234567890',
    'wordLists': [],
    'id': 1,
    'isActive': True
}

TEST_USER_2 = {
    'name': 'Test User 2',
    'email': USER_EMAIL_2,
    'phone': '1234567890',
    'wordLists': [],
    'password': 'testpassword'
}

TEST_USER_2_RESPONSE = {
    'name': 'Test User 2',
    'email': USER_EMAIL_2,
    'phone': '1234567890',
    'wordLists': [],
    'id': 2,
    'isActive': True
}

UPDATED_TEST_USER = {
    "email": UPDATED_EMAIL,
    "isActive": False,
    "name": "New Name",
    "password": "newpassword",
    "phone": "1234567890"
}

UPDATED_TEST_USER_RESPONSE = {'name': 'New Name',
                              'email': 'test@gmail.com',
                              'phone': '1234567890',
                              'wordLists': [],
                              'id': 1,
                              'isActive': True
                              }


TOPIC1 = "Science"
TOPIC2 = "Technology"
UPDATED_TOPIC1 = "Science and Technology"

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
    "at",
    "x",
    "",
    "Unknown",
    "Killing",
    "Drug Abuse",
    "xyz",
]

INVALID_WORDS_TO_UPDATE = [
    {
        "id": -999,  # invalid id
        "word": "string",
        "definition": "string",
        "rootOrigin": "string",
        "usage": "string",
        "languageOrigin": "string",
        "partsOfSpeech": "string",
        "alternatePronunciation": "string",
        "audioUrl": "string",
        "wordListId": 1
    },
    {
        "id": 1,
        "word": "string",
        "definition": "string",
        "rootOrigin": "string",
        "usage": "string",
        "languageOrigin": "string",
        "partsOfSpeech": "string",
        "alternatePronunciation": "string",
        "audioUrl": "string",
        "wordListId": -999  # invalid id
    },
    {
        "id": 1,
        "word": "Child Abuse",  # Inappropriate word
        "definition": "string",
        "rootOrigin": "string",
        "usage": "string",
        "languageOrigin": "string",
        "partsOfSpeech": "string",
        "alternatePronunciation": "string",
        "audioUrl": "string",
        "wordListId": 1
    },
    {
        "id": 1,
        "word": "",  # Invalid word
        "definition": "string",
        "rootOrigin": "string",
        "usage": "string",
        "languageOrigin": "string",
        "partsOfSpeech": "string",
        "alternatePronunciation": "string",
        "audioUrl": "string",
        "wordListId": 1
    }
]

INVALID_WORD_LISTS_TO_UPDATE = [
    # First 2 are invalid ids
    {
        "id": -999,
        "title": "Test update title"
    },
    {
        "id": 999,
        "title": "Test update title"
    },
    # Invalid title
    {
        "id": 1,
        "title": "Child Abuse"  # Inappropriate title
    },
    # Invalid length
    {
        "id": 1,
        "title": ""  # Empty
    },
    {
        "id": 1,
        "title": "A"  # Too short
    },
    # Repeat of existing title
    {
        "id": 1,
        "title": CUSTOM_WORD_LIST_TITLE  # Already exists
    }
]

IRRELEVANT_WORDS = [
    "Tree", "Book", "Flower", "Sunset", "Rainbow", "123", "abc", "xyz", "abc123", "123abc", "abcxyz", "xyzabc", 123, 999, -999
]

CUSTOM_WORD_LIST = {
    "title": CUSTOM_WORD_LIST_TITLE,
    "words": [
        {
            "word": CUSTOM_WORDS[0],
            "definition": "string",
            "rootOrigin": "string",
            "usage": "string",
            "languageOrigin": "string",
            "partsOfSpeech": "string",
            "alternatePronunciation": "string"
        },
        {
            "word": CUSTOM_WORDS[1],
            "definition": "string",
            "rootOrigin": "string",
            "usage": "string",
            "languageOrigin": "string",
            "partsOfSpeech": "string",
            "alternatePronunciation": "string"
        },
        {
            "word": CUSTOM_WORDS[2],
            "definition": "string",
            "rootOrigin": "string",
            "usage": "string",
            "languageOrigin": "string",
            "partsOfSpeech": "string",
            "alternatePronunciation": "string"
        }
    ]
}

CUSTOM_WORD_LIST_EXTRA = {
    "title": CUSTOM_WORD_LIST_TITLE,
    "words": [
        {
            "word": CUSTOM_WORDS[2],  # Repeated
            "definition": "string",
            "rootOrigin": "string",
            "usage": "string",
            "languageOrigin": "string",
            "partsOfSpeech": "string",
            "alternatePronunciation": "string"
        },
        {
            "word": CUSTOM_WORDS[3],
            "definition": "string",
            "rootOrigin": "string",
            "usage": "string",
            "languageOrigin": "string",
            "partsOfSpeech": "string",
            "alternatePronunciation": "string"
        }
    ]
}

EMPTY_WORD_LIST = {
    "title": "Software",
    "words": []
}

INVALID_CUSTOM_LISTS = [
    {
        "title": "Drug",
        "words": []
    },
    {
        "title": "",
        "words": []
    },
    {
        "title": "A",
        "words": []
    },
    {
        "title": "AB",
        "words": []
    },
    {
        "title": "String",
        "words": [{
            "word": "drug",  # Inappropriate word
            "definition": "string",
            "rootOrigin": "string",
            "usage": "string",
            "languageOrigin": "string",
            "partsOfSpeech": "string",
            "alternatePronunciation": "string"
        }]
    },
    {
        "title": "University",
        "words": [
            {  # Missing field: rootOrigin and word
                "definition": "string",
                "usage": "string",
                "languageOrigin": "string",
                "partsOfSpeech": "string",
                "alternatePronunciation": "string"
            }
        ]
    },
    {
        "title": "University",
        "words": [
            {
                "word": "",  # Invalid length
                "definition": "string",
                "rootOrigin": "string",
                "usage": "string",
                "languageOrigin": "string",
                "partsOfSpeech": "string",
                "alternatePronunciation": "string"
            },
        ]
    }
]
