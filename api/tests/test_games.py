from fastapi.testclient import TestClient
from api.main import app
from api.tests.helpers import *

client = TestClient(app)

headers_user_1 = {}  # JWT for user 1
word_list_user_1 = {}  # Word list for user 1
stations_ids_user_1 = []
STATIONS_PER_ROUTE = 8


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


def test_retrieve_games():
    global stations_ids_user_1
    word_list_id = word_list_user_1.get("id")
    assert word_list_id != None

    response = client.post(
        f"/games/?word_list_id={word_list_id}", headers=headers_user_1)
    assert response.status_code == 200
    assert len(response.json()) == STATIONS_PER_ROUTE
    for i in range(STATIONS_PER_ROUTE):
        assert response.json()[i].get("route") == 1
        assert response.json()[i].get("level") == i + 1
        assert response.json()[i].get("isCompleted") == False
        stations_ids_user_1.append(response.json()[i].get("id"))


def test_mark_station_as_completed():
    # Mark all stations as completed
    for station_id in stations_ids_user_1:
        response = client.patch(
            f"/games/stations/{station_id}", headers=headers_user_1)
        assert response.status_code == 200
        assert response.json().get("isCompleted") == True


def test_retrieve_games_for_next_route():
    response = client.post(
        f"/games/next-route?game_id={1}", headers=headers_user_1)
    assert response.status_code == 200
    # Add more assertions based on your expected response data


def test_delete_users():
    # Delete user 1
    response = client.delete("/users/", headers=headers_user_1)
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL
