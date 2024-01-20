from fastapi.testclient import TestClient
from api.main import app
from api.tests.helpers import USER_EMAIL, TEST_USER, UPDATED_TEST_USER

client = TestClient(app)

# Create a test user
user_id = -999


def test_create_user():
    global user_id
    # Test creating the user
    response = client.post("/users/", json=TEST_USER.model_dump())
    user_id = response.json().get("id")
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL
    assert user_id != -999


def test_create_duplicate_user():
    # Test creating a duplicate user
    response = client.post("/users/", json=TEST_USER.model_dump())
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


def test_get_user():
    global user_id
    # Test retrieving a non-existent user
    response = client.get("/users/-999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    # Test retrieving the user by ID
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() != {"detail": "User not found"}

    # Test retrieving the user by email
    response = client.get(f"/users/email/{USER_EMAIL}")
    assert response.status_code == 200
    assert response.json() != {"detail": "User not found"}


def test_update_user():
    global user_id
    # Test updating all fields
    response = client.put("/users",
                          json=UPDATED_TEST_USER)
    assert response.status_code == 200
    assert response.json().get("email") == UPDATED_TEST_USER['email']
    assert response.json().get("isActive") == UPDATED_TEST_USER['isActive']
    assert response.json().get("name") == UPDATED_TEST_USER['name']
    assert response.json().get("phone") == UPDATED_TEST_USER['phone']

    # Test updating the email
    response = client.put("/users", json={"email": USER_EMAIL})
    assert response.status_code == 200
    assert response.json().get("email") == USER_EMAIL

    # Test updating the active status to False
    response = client.put("/users", json={"isActive": False})
    assert response.status_code == 200
    assert response.json().get("isActive") == False

    # Test updating the active status to True
    response = client.put("/users", json={"isActive": True})
    assert response.status_code == 200
    assert response.json().get("isActive") == True


def test_delete_user_with_invalid_email():
    # Invalid email
    response = client.delete("/users/?user_email=-999")
    assert response.status_code == 422
    assert response.json().get("detail")[0].get("type") == "value_error"


def test_delete_user_with_email():
    # Test deleting a user by email
    response = client.delete(f"/users/?user_email={USER_EMAIL}")
    assert response.status_code == 200
    assert response.json() != {"detail": "User not found"}


def test_delete_user_with_no_id_or_email():
    # Test deleting a user with no ID or email
    response = client.delete("/users/")
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Either user_id or user_email must be provided"}


def test_delete_user_with_id():
    # Test deleting a user by ID
    test_create_user()
    global user_id
    # Test deleting a user by ID
    response = client.delete(f"/users/?user_id={user_id}")
    assert response.status_code == 200
    assert response.json() != {"detail": "User not found"}
