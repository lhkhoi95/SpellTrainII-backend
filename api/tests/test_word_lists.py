import random
from fastapi.testclient import TestClient
from api.main import app
from .helpers import *

client = TestClient(app)


headers_user_1 = {}  # JWT for user 1
headers_user_2 = {}  # JWT for user 2
word_list_user_1 = {}  # Word list for user 1
word_list_2 = {}  # Second word list for user 1
word_list_user_2 = {}  # Word list for user 2


def test_create_user_1():
    # Test creating the user
    response = client.post("/users/", json=TEST_USER)
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL


def test_login_user_1():
    global headers_user_1
    response = client.post(
        "/users/login", json={"email": TEST_USER["email"], "password": TEST_USER["password"]})
    accessToken = response.json().get("accessToken")
    headers_user_1 = {"Authorization": f"Bearer {accessToken}"}
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL
    assert headers_user_1 != {}


def test_create_user2():
    # Test creating the second user
    response = client.post("/users/", json=TEST_USER_2)
    assert response.status_code == 200
    assert response.json() == TEST_USER_2_RESPONSE


def test_login_user_2():
    global headers_user_2
    response = client.post(
        "/users/login", json={"email": TEST_USER_2["email"], "password": TEST_USER_2["password"]})
    accessToken = response.json().get("accessToken")
    headers_user_2 = {"Authorization": f"Bearer {accessToken}"}
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL_2
    assert headers_user_2 != {}


def test_create_generative_word_list_invalid_topic():
    for invalid_topic in INVALID_TOPICS:
        response = client.get(
            f"/word-lists/?topic={invalid_topic}", headers=headers_user_1)
        assert response.status_code in [400, 422]
        # Invalid title length
        if response.status_code == 422:
            assert response.json().get("detail")[0].get(
                "msg") == INVALID_TITLE_LENGTH_MSG
        # Inappropriate topic
        if response.status_code == 400:
            assert len(response.json().get("detail")) > 0


def test_user_1_create_generative_word_list():
    global word_list_user_1
    response1 = client.get(
        f"/word-lists/?topic={TOPIC1}", headers=headers_user_1)
    word_list_user_1 = response1.json()
    assert word_list_user_1 != {}
    assert response1.status_code == 200

    # The alternative pronunciation, definition, etc. should be empty strings except for word, wordListId, audioUrl, and id.
    for word in word_list_user_1.get("words"):
        assert word.get("word") != ""
        assert all(value == "" for key, value in word.items()
                   if not key in ['word', 'wordListId', 'id', 'audioUrl', 'isAIGenerated'])
    assert response1.json() != {"detail": "Word list not found"}
    assert response1.json().get('ownerId') == 1
    assert response1.json().get("isAIGenerated") == True

    # Test getting a word list by the same topic (should be faster)
    response2 = client.get(
        f"/word-lists/?topic={TOPIC1}", headers=headers_user_1)
    assert response2.status_code == 200
    assert response1.json() == response2.json()
    assert response1.json().get("isAIGenerated") == True

    # Test no duplicate words in the word list
    word_objects = response2.json().get("words")
    words = [word_obj.get("word") for word_obj in word_objects]
    assert len(words) == len(set(words))


def test_user_2_create_generative_word_list():
    global word_list_user_2
    response = client.get(
        f"/word-lists/?topic={TOPIC1}", headers=headers_user_2)
    word_list_user_2 = response.json()
    assert response.json() != {}
    assert response.json() != {"detail": "Word list not found"}
    assert response.json().get('ownerId') == 2
    assert response.json().get("isAIGenerated") == True
    assert response.status_code == 200

    # The alternative pronunciation, definition, etc. should be empty strings except for word, wordListId, audioUrl, and id.
    for word in response.json().get("words"):
        assert word.get("word") != ""
        assert all(value == "" for key, value in word.items()
                   if not key in ['word', 'wordListId', 'id', 'audioUrl', 'isAIGenerated'])

    # Test no duplicate words in the word list
    word_objects = response.json().get("words")
    words = [word_obj.get("word") for word_obj in word_objects]
    assert len(words) == len(set(words))


def test_user_1_create_custom_word_list():
    # Create a new list with some words in it
    response = client.put(
        f"word-lists/", json=CUSTOM_WORD_LIST, headers=headers_user_1)
    word_objs = response.json().get("words")
    for word_obj in word_objs:
        assert word_obj.get("word") in CUSTOM_WORDS
        assert word_obj.get("audioUrl") != ""
        assert word_obj.get("isAIGenerated") == False

    # Add some new words including repeated words.
    response = client.put(
        f"word-lists/", json=CUSTOM_WORD_LIST_EXTRA, headers=headers_user_1)
    word_objs = response.json().get("words")
    for word_obj in word_objs:
        assert word_obj.get("word") in CUSTOM_WORDS
        assert word_obj.get("audioUrl") is not None
        assert word_obj.get("isAIGenerated") == False
    assert len(response.json().get("words")) == len(CUSTOM_WORDS)

    # Create a new word list with empty words
    response = client.put(
        f"word-lists/", json=EMPTY_WORD_LIST, headers=headers_user_1)
    word_objs = response.json().get("words")
    assert len(word_objs) == 0


def test_user_1_create_invalid_word_list():
    for invalid_word_list in INVALID_CUSTOM_LISTS:
        response = client.put(
            f"word-lists/", json=invalid_word_list, headers=headers_user_1)
        assert response.status_code in [400, 422]


def test_get_word_list_by_id():
    # Test getting a word list by ID
    global word_list_user_1
    word_list_id = word_list_user_1.get("id")
    assert word_list_id is not None

    # Test getting the word list by ID
    response = client.get(
        f"/word-lists/{word_list_id}", headers=headers_user_1)
    assert response.status_code == 200
    assert response.json().get("id") == word_list_id
    assert response.json().get("ownerId") == TEST_USER_RESPONSE.get("id")

    # Get the word list that does not exist.
    response = client.get(
        "/word-lists/-999", headers=headers_user_1)
    assert response.status_code == 404
    assert response.json() == {"detail": "Word list not found"}

    # Get the word list that does not belong to the user 1
    invalid_id = word_list_user_2.get("id")
    response = client.get(
        f"/word-lists/{invalid_id}", headers=headers_user_1)
    assert response.status_code == 404
    assert response.json() == {"detail": "Word list not found"}


def test_create_generative_word_list_no_topic():
    # Test creating a generative word list without providing a topic
    response = client.get("/word-lists/", headers=headers_user_1)
    assert response.json().get("detail")[0].get("msg") == "Field required"
    assert response.status_code == 422


def test_get_all_by_uid():
    # Test getting all word lists by user ID
    response = client.get("/word-lists/get-all", headers=headers_user_1)
    assert response.status_code == 200
    # 2 custom word lists and 1 generative word list
    assert len(response.json()) == 3


def test_add_more_words_to_word_list():
    # Test adding more words to a word list
    word_list_id = word_list_user_1.get("id")
    assert word_list_id is not None

    response = client.get(
        f"/word-lists/{word_list_id}/more", headers=headers_user_1)
    assert response.status_code == 200
    assert len(response.json().get("words")) > len(
        word_list_user_1.get("words"))
    for word_obj in response.json().get("words"):
        assert word_obj.get("isAIGenerated") == True


def test_get_word_info():
    # Test for invalid word_id
    for word_id in INVALID_INT_IDS:
        response = client.get(
            f"/word-lists/words/{word_id}", headers=headers_user_1)

        assert response.status_code == 404
        assert response.json() == {"detail": f"Word ID {word_id} not found"}

    # Test cannot get word info from another user_2's word list
    user_2_word_id = word_list_user_2.get("words")[0].get("id")
    response = client.get(
        f"/word-lists/words/{user_2_word_id}", headers=headers_user_1)
    assert response.status_code == 404
    assert response.json() == {"detail": f"Word list not found"}

    # Select 5 random words from the word list to test
    words = word_list_user_1.get("words")
    assert len(words) > 0
    indexes = random.sample(range(0, len(words)), 5)

    for i in indexes:
        word = words[i]
        # Fetch the word the first time
        response = client.get(
            f"/word-lists/words/{word.get('id')}", headers=headers_user_1)
        assert response.status_code == 200
        assert response.json().get("word") == word.get("word")

        # Fetch the second time, should be faster
        response = client.get(
            f"/word-lists/words/{word.get('id')}", headers=headers_user_1)
        assert response.status_code == 200
        assert response.json().get("word") == word.get("word")


def test_update_words():
    words = word_list_user_1.get("words")

    # Select 5 random words from the word list to test
    indexes = random.sample(range(0, len(words)), 5)

    for i in indexes:
        word = words[i]
        word["definition"] = "Test definition"
        word["rootOrigin"] = "Test root origin"
        word["usage"] = "Test usage"
        word["languageOrigin"] = "Test language origin"
        word["partsOfSpeech"] = "Test parts of speech"
        word["alternatePronunciation"] = "Test alternate pronunciation"

    # Update the words
    response = client.patch("/word-lists/words",
                            json=words, headers=headers_user_1)

    assert response.status_code == 200
    assert len(response.json()) == len(words)


def test_update_invalid_words():
    # Invalid word ID
    word_id = INVALID_WORDS_TO_UPDATE[0].get("id")
    response = client.patch("/word-lists/words",
                            json=[INVALID_WORDS_TO_UPDATE[0]], headers=headers_user_1)
    assert response.status_code == 404
    assert response.json() == {"detail": f"Word ID {word_id} not found"}

    # Invalid word list ID
    response = client.patch("/word-lists/words",
                            json=[INVALID_WORDS_TO_UPDATE[1]], headers=headers_user_1)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Word list not found"}

    # Invalid word content
    response = client.patch("/word-lists/words",
                            json=[INVALID_WORDS_TO_UPDATE[2]], headers=headers_user_1)
    invalid_word = INVALID_WORDS_TO_UPDATE[2].get("word")
    assert response.status_code == 400
    assert response.json().get(
        "detail") == f"{invalid_word} is not a valid word."

    # Empty word content
    response = client.patch("/word-lists/words",
                            json=[INVALID_WORDS_TO_UPDATE[3]], headers=headers_user_1)
    assert response.status_code == 422
    assert response.json().get("detail")[0].get(
        "msg") == INVALID_WORD_LENGTH_MSG


def test_delete_words_invalid_word_id():
    # Test deleting words with invalid word ID
    word_ids_to_delete = INVALID_STR_IDS

    response = client.delete(
        "/word-lists/words/",
        params={"word_ids": word_ids_to_delete},
        headers=headers_user_1
    )

    assert response.status_code == 422
    assert response.json().get("detail")[0].get("type") == "int_parsing"


def test_delete_words():
    words = word_list_user_1.get("words")
    assert len(words) > 0

    word_ids_to_delete = [word.get("id") for word in words]

    # Pass the word IDs as a Query parameter (localhost:8000/word-lists/words/?word_ids=1&word_ids=2&word_ids=3)
    response = client.delete(
        "/word-lists/words/",
        params={"word_ids": word_ids_to_delete},
        headers=headers_user_1
    )
    assert response.status_code == 200
    assert len(response.json()) == len(word_ids_to_delete)


def test_update_invalid_word_list():
    length = len(INVALID_WORD_LISTS_TO_UPDATE)
    # Invalid IDs (first 2 elements)
    for invalid_word_list in INVALID_WORD_LISTS_TO_UPDATE[:2]:
        response = client.patch(
            "/word-lists/", json=invalid_word_list, headers=headers_user_1)
        assert response.status_code == 404
        assert response.json() == {"detail": "Word list not found"}

    # Inappropriate word content (third element)
    invalid_word_list = INVALID_WORD_LISTS_TO_UPDATE[2]
    response = client.patch(
        "/word-lists/", json=invalid_word_list, headers=headers_user_1)
    assert response.status_code == 400
    assert len(response.json().get("detail")) > 0

    # Invalid length (fourth, fifth elements)
    for invalid_word_list in INVALID_WORD_LISTS_TO_UPDATE[3:length-1]:
        response = client.patch(
            "/word-lists/", json=invalid_word_list, headers=headers_user_1)
        assert response.status_code == 422
        assert response.json().get("detail")[0].get(
            "msg") == INVALID_TITLE_LENGTH_MSG

    # Repeated title (last element)
    response = client.patch(
        "/word-lists/", json=INVALID_WORD_LISTS_TO_UPDATE[-1], headers=headers_user_1)
    assert response.status_code == 400
    assert response.json().get("detail") == "Word list with the same title already exists."


def test_update_word_list():
    word_list_id = word_list_user_1.get("id")
    assert word_list_id is not None

    # Update with unchanged title
    response = client.patch(
        "/word-lists/", json=word_list_user_1, headers=headers_user_1)
    assert response.status_code == 200
    assert response.json().get("title") == word_list_user_1["title"]

    # Update with a new title
    word_list_user_1["title"] = UPDATED_TOPIC1
    response = client.patch(
        "/word-lists/", json=word_list_user_1, headers=headers_user_1)
    assert response.status_code == 200
    assert response.json().get("title") == word_list_user_1["title"]


def test_delete_invalid_word_list():
    # Test deleting an invalid word list
    for invalid_word_list_id in INVALID_INT_IDS:
        response = client.delete(f"/word-lists/", params={
            "word_list_id": invalid_word_list_id}, headers=headers_user_1)

        assert response.status_code == 404
        assert response.json() == {"detail": "Word list not found"}


def test_delete_word_list():
    word_list_id = word_list_user_1.get("id")
    assert word_list_id is not None

    response = client.delete(f"/word-lists/", params={
        "word_list_id": word_list_id}, headers=headers_user_1)

    assert response.status_code == 200
    assert response.json().get("id") == word_list_id


def test_create_generative_word_list_2():
    global word_list_2
    # Test creating a generative word list for a new topic
    response = client.get(
        f"/word-lists/?topic={TOPIC2}", headers=headers_user_1)
    word_list_2 = response.json()
    assert response.status_code == 200
    assert response.json() != {"detail": "Word list not found"}


def test_delete_words_from_word_list_2():
    words = word_list_2.get("words")
    assert len(words) > 0

    word_ids_to_delete = [word.get("id") for word in words]

    response = client.delete(
        "/word-lists/words/",
        params={"word_ids": word_ids_to_delete},
        headers=headers_user_1
    )
    assert response.status_code == 200
    assert len(response.json()) == len(word_ids_to_delete)


def test_add_invalid_words_to_word_list_2():
    word_list_id = word_list_2.get("id")
    assert word_list_id is not None
    # Topic: Technology
    for invalid_word in IRRELEVANT_WORDS:
        word = {"word": str(invalid_word), "wordListId": word_list_id}
        response = client.post("/word-lists/words",
                               json=[word], headers=headers_user_1)
        assert response.status_code == 400
        assert response.json().get(
            "detail") == f"{invalid_word} is not a valid word."

    # Test adding a word with an invalid word list ID
    for invalid_word_list_id in INVALID_INT_IDS:
        word = {"word": "test", "wordListId": invalid_word_list_id}
        response = client.post("/word-lists/words",
                               json=[word], headers=headers_user_1)
        assert response.status_code == 404
        assert response.json().get("detail") == "Word list not found"


def test_add_words_to_word_list_2():
    word_list_id = word_list_2.get("id")
    assert word_list_id is not None

    # Test adding a valid word related to the topic Science
    for tech_word in TECH_WORDS:
        word = {"word": tech_word, "wordListId": word_list_id}
        response = client.post("/word-lists/words",
                               json=[word], headers=headers_user_1)
        assert response.status_code == 200
        # Check if the word was added to the word list
        new_word_list = response.json().get("words")
        assert word.get("word") in [word.get("word") for word in new_word_list]

    # Test adding a repeated word
    for tech_word in TECH_WORDS_WITH_SPACES:
        word = {"word": tech_word, "wordListId": word_list_id}
        response = client.post("/word-lists/words",
                               json=[word], headers=headers_user_1)
        assert response.status_code == 400
        assert response.json().get(
            "detail") == f"{tech_word} already exists in the word list."


def test_delete_users():
    # Delete user 1
    response = client.delete("/users/", headers=headers_user_1)
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL

    # Delete user 2
    response = client.delete("/users/", headers=headers_user_2)
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL_2
