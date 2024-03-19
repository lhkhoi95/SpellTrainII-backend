from fastapi.testclient import TestClient
from api.main import app
from api.tests.helpers import *

client = TestClient(app=app)

# header to store jwt token for sub-sequence requests
headers = {}


def test_create_user():
    # Test creating the user
    response = client.post("/users/", json=TEST_USER)
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL

    # Test creating a duplicate user
    response = client.post("/users/", json=TEST_USER)
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


def test_login():
    global headers
    response = client.post(
        "/users/login", json={"email": TEST_USER["email"], "password": TEST_USER["password"]})
    accessToken = response.json().get("accessToken")
    headers = {"Authorization": f"Bearer {accessToken}"}
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL
    assert headers != {}


def test_get_user():
    # Without access token
    response = client.get("/users/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

    # Using incorrect token
    fakeToken = "xasbcyuihwgbui2390jcdsm"
    response = client.get(
        f"/users/", headers={"Authorization": f"Bearer {fakeToken}"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid token or expired token."}

    # Using correct token
    response = client.get(f"/users/", headers=headers)
    assert response.status_code == 200
    assert response.json() == TEST_USER_RESPONSE


def test_update_user():
    # Test updating all fields
    response = client.put("/users",
                          json=UPDATED_TEST_USER, headers=headers)
    assert response.status_code == 200
    assert response.json().get("email") == UPDATED_TEST_USER['email']
    assert response.json().get("isActive") == UPDATED_TEST_USER['isActive']
    assert response.json().get("name") == UPDATED_TEST_USER['name']
    assert response.json().get("phone") == UPDATED_TEST_USER['phone']

    # Test updating the email
    response = client.put(
        "/users", json={"email": USER_EMAIL}, headers=headers)
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL

    # Test updating the active status to False
    response = client.put(
        "/users", json={"isActive": False}, headers=headers)
    assert response.status_code == 200
    assert response.json().get("isActive") == False

    # Test updating the active status to True
    response = client.put(
        "/users", json={"isActive": True}, headers=headers)
    assert response.status_code == 200
    assert response.json().get("isActive") == True


def test_delete_user():
    response = client.delete("/users/", headers=headers)
    assert response.status_code == 200
    assert response.json() == UPDATED_TEST_USER_RESPONSE
