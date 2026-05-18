from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
original_activities = deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_activity_list():
    reset_activities()

    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_new_participant():
    reset_activities()

    email = "testuser@example.com"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_duplicate_signup_returns_bad_request():
    reset_activities()

    email = "emma@mergington.edu"
    response = client.post(
        "/activities/Programming Class/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities["Programming Class"]["participants"].count(email) == 1


def test_delete_participant_removes_student():
    reset_activities()

    email = "john@mergington.edu"
    response = client.delete(
        "/activities/Gym Class/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Gym Class"
    assert email not in activities["Gym Class"]["participants"]


def test_delete_missing_participant_returns_not_found():
    reset_activities()

    email = "missing@student.edu"
    response = client.delete(
        "/activities/Gym Class/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
