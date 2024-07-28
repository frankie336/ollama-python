from starlette.testclient import TestClient
from api.app import create_test_app

app = create_test_app()
client = TestClient(app)

def test_create_thread():
    # Test data
    thread_data = {
        "participant_ids": []
    }

    # Create users
    user1 = client.post("/v1/users", json={"name": "User 1"})
    user2 = client.post("/v1/users", json={"name": "User 2"})

    assert user1.status_code == 200
    assert user2.status_code == 200

    user1_data = user1.json()
    user2_data = user2.json()

    # Update thread data with actual user IDs
    thread_data['participant_ids'] = [user1_data['id'], user2_data['id']]

    # Send POST request to create thread
    response = client.post("/v1/threads", json=thread_data)

    # Check response
    assert response.status_code == 200
    created_thread = response.json()
    assert created_thread["object"] == "thread"
    assert len(created_thread["participants"]) == 2
    assert created_thread["participants"][0]["id"] in thread_data["participant_ids"]
    assert created_thread["participants"][1]["id"] in thread_data["participant_ids"]

def test_create_thread_invalid_users():
    # Test data with invalid user IDs
    thread_data = {
        "participant_ids": ["invalid_user_id_1", "invalid_user_id_2"]
    }

    # Send POST request to create thread
    response = client.post("/v1/threads", json=thread_data)

    # Check response
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid user IDs"
