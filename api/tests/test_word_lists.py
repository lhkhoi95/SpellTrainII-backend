import json
import random
from fastapi.testclient import TestClient
from api.main import app
from .helpers import *

client = TestClient(app)

user_id = -999
word_list = {}
word_list_2 = {}


def test_create_a_user():
    # Create a test user to hold the word lists
    global user_id
    response = client.post("/users/", json=TEST_USER.model_dump())
    user_id = response.json().get("id")

    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL
    assert user_id != -999


def test_create_generative_word_list_invalid_topic():
    # Test creating a generative word list for an invalid topic
    for invalid_topic in INVALID_TOPICS:
        response = client.get(f"/word-lists/?topic={invalid_topic}")
        assert response.status_code == 400
        if response.status_code == 200:
            assert len(response.json().get("words")) > 0
            # Check for non-duplicate words
            assert len(response.json().get("words")) == len(
                set(response.json().get("words")))
        if response.status_code == 400:
            assert response.json().get("detail") is not None


def test_create_generative_word_list():
    global word_list

    # Test getting a word list by topic
    response1 = client.get(f"/word-lists/?topic={TOPIC1}")
    word_list = response1.json()
    assert word_list != {}
    assert response1.status_code == 200
    # Each field should be empty except for the word field
    for word in word_list.get("words"):
        assert word.get("word") != ""
        assert word.get("definition") == ""
        assert word.get("rootOrigin") == ""
        assert word.get("usage") == ""
        assert word.get("languageOrigin") == ""
        assert word.get("partsOfSpeech") == ""
        assert word.get("alternatePronunciation") == ""
    assert response1.json() != {"detail": "Word list not found"}

    # Test getting a word list by the same topic (should be faster)
    response2 = client.get(f"/word-lists/?topic={TOPIC1}")
    assert response2.status_code == 200
    assert response1.json() == response2.json()


def test_get_word_list_by_id():
    # Test getting a word list by ID
    global word_list
    word_list_id = word_list.get("id")
    assert word_list_id is not None

    response = client.get(f"/word-lists/{word_list_id}")
    assert response.status_code == 200


def test_create_generative_word_list_no_topic():
    # Test creating a generative word list without providing a topic
    response = client.get("/word-lists/")
    assert response.json().get("detail")[0].get("msg") == "Field required"
    assert response.status_code == 422


def test_get_all_by_uid():
    # Test getting all word lists by user ID
    response = client.get("/word-lists/get-all")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_add_more_words_to_word_list():
    # Test adding more words to a word list
    global word_list
    word_list_id = word_list.get("id")
    assert word_list_id is not None

    response = client.get(f"/word-lists/{word_list_id}/more")
    assert response.status_code == 200
    assert len(response.json().get("words")) > 0


def test_get_word_info():
    global word_list
    # Test for invalid word_id
    for word_id in INVALID_INT_IDS:
        response = client.get(f"/word-lists/words/{word_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": f"Word ID {word_id} not found"}

    # Select 5 random words from the word list to test
    words = word_list.get("words")
    assert len(words) > 0
    indexes = random.sample(range(0, len(words)), 5)

    for i in indexes:
        word = words[i]
        # Fetch the word the first time
        response = client.get(f"/word-lists/words/{word.get('id')}")
        assert response.status_code == 200
        assert response.json().get("word") == word.get("word")

        # Fetch the second time, should be faster
        response = client.get(f"/word-lists/words/{word.get('id')}")
        assert response.status_code == 200
        assert response.json().get("word") == word.get("word")


def test_update_words():
    global word_list

    words = word_list.get("words")

    # Update all words
    for word_to_update in words:
        word_to_update["definition"] = "Test update definition"
        word_to_update["rootOrigin"] = "Test update root origin"
        word_to_update["usage"] = "Test update usage"
        word_to_update["languageOrigin"] = "Test update language origin"
        word_to_update["partsOfSpeech"] = "Test update parts of speech"
        word_to_update["alternatePronunciation"] = "Test update alternate pronunciation"

    # Update the words
    response = client.patch("/word-lists/words", json=words)

    assert response.status_code == 200
    assert len(response.json()) == len(words)


def test_update_invalid_words():
    # Test updating invalid words
    word_id = INVALID_WORD[0].get("id")
    response = client.patch("/word-lists/words", json=INVALID_WORD)
    assert response.status_code == 404
    assert response.json() == {"detail": f"Word ID {word_id} not found"}

    response = client.patch("/word-lists/words", json=INVALID_WORD_LIST_ID)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Word does not belong to the word list"}


def test_delete_words_invalid_word_id():
    # Test deleting words with invalid word ID
    word_ids_to_delete = INVALID_IDS

    response = client.delete(
        "/word-lists/words/",
        params={"word_ids": word_ids_to_delete}
    )

    assert response.status_code == 422
    assert response.json().get("detail")[0].get("type") == "int_parsing"


def test_delete_words():
    global word_list

    words = word_list.get("words")
    assert len(words) > 0

    word_ids_to_delete = [word.get("id") for word in words]

    # Pass the word IDs as a Query parameter (localhost:8000/word-lists/words/?word_ids=1&word_ids=2&word_ids=3)
    response = client.delete(
        "/word-lists/words/",
        params={"word_ids": word_ids_to_delete}
    )
    assert response.status_code == 200
    assert len(response.json()) == len(word_ids_to_delete)


def test_update_invalid_word_list():
    # Test updating an invalid word list
    for invalid_word_list in INVALID_WORD_LISTS_TO_UPDATE:
        response = client.patch("/word-lists/", json=invalid_word_list)
        assert response.status_code == 404
        assert response.json() == {"detail": "Word list not found"}


def test_update_word_list():
    # Test updating a word list
    global word_list
    word_list_id = word_list.get("id")
    assert word_list_id is not None

    word_list["title"] = "Test update title"

    response = client.patch("/word-lists/", json=word_list)
    assert response.status_code == 200
    assert response.json().get("title") == word_list["title"]


def test_delete_invalid_word_list():
    # Test deleting an invalid word list
    for invalid_word_list_id in INVALID_INT_IDS:
        response = client.delete(f"/word-lists/", params={
            "word_list_id": invalid_word_list_id})

        assert response.status_code == 404
        assert response.json() == {"detail": "Word list not found"}


def test_delete_word_list():
    # Test deleting a word list
    global word_list
    word_list_id = word_list.get("id")
    assert word_list_id is not None

    response = client.delete(f"/word-lists/", params={
        "word_list_id": word_list_id})

    assert response.status_code == 200
    assert response.json().get("id") == word_list_id


def test_create_generative_word_list_2():
    global word_list_2
    # Test creating a generative word list for a new topic
    response = client.get(f"/word-lists/?topic={TOPIC2}")
    word_list_2 = response.json()
    assert response.status_code == 200
    assert response.json() != {"detail": "Word list not found"}


def test_delete_words_from_word_list_2():
    global word_list_2

    words = word_list_2.get("words")
    assert len(words) > 0

    word_ids_to_delete = [word.get("id") for word in words]

    response = client.delete(
        "/word-lists/words/",
        params={"word_ids": word_ids_to_delete}
    )
    assert response.status_code == 200
    assert len(response.json()) == len(word_ids_to_delete)


def test_add_invalid_words_to_word_list_2():
    # Test adding a word
    global word_list_2
    word_list_id = word_list_2.get("id")
    assert word_list_id is not None
    # Topic: Technology
    for invalid_word in IRRELEVANT_WORDS:
        word = {"word": str(invalid_word), "wordListId": word_list_id}
        response = client.post("/word-lists/words", json=word)
        assert response.status_code == 400
        assert response.json().get("detail") == "This is not a valid word."

    # Test adding a word with an invalid word list ID
    for invalid_word_list_id in INVALID_INT_IDS:
        word = {"word": "test", "wordListId": invalid_word_list_id}
        response = client.post("/word-lists/words", json=word)
        assert response.status_code == 404
        assert response.json().get("detail") == "Word list not found"


def test_add_words_to_word_list_2():
    # Test adding a word
    global word_list_2
    word_list_id = word_list_2.get("id")
    assert word_list_id is not None

    # Test adding a valid word related to the topic Science
    for tech_word in TECH_WORDS:
        word = {"word": tech_word, "wordListId": word_list_id}
        response = client.post("/word-lists/words", json=word)
        assert response.status_code == 200
        # Check if the word was added to the word list
        new_word_list = response.json().get("words")
        assert word.get("word") in [word.get("word") for word in new_word_list]

    # Test adding a repeated word
    for tech_word in TECH_WORDS_WITH_SPACES:
        word = {"word": tech_word, "wordListId": word_list_id}
        response = client.post("/word-lists/words", json=word)
        assert response.status_code == 400
        assert response.json().get("detail") == "This word already exists in the word list."


def test_delete_a_user():
    # Remove the test user at the end of the tests
    global user_id
    response = client.delete(f"/users/", params={"user_id": user_id})
    assert response.status_code == 200
    assert response.json() != {"detail": "User not found"}
