from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

ORIGINAL_ACTIVITIES = deepcopy(activities)


def restore_activities():
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_data():
    restore_activities()

    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_adds_email_to_activity():
    restore_activities()
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    response = client.post(f"/activities/{activity}/signup?email={email}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Signed up {email} for {activity}"

    activities_payload = client.get("/activities").json()
    assert email in activities_payload[activity]["participants"]


def test_duplicate_signup_is_rejected():
    restore_activities()
    activity = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity}/signup?email={email}")

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_unregister_removes_email_from_activity():
    restore_activities()
    activity = "Chess Club"
    email = "newstudent2@mergington.edu"

    client.post(f"/activities/{activity}/signup?email={email}")

    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"

    activities_payload = client.get("/activities").json()
    assert email not in activities_payload[activity]["participants"]


def test_unknown_activity_returns_404():
    restore_activities()

    response = client.get("/activities/Unknown Activity")
    assert response.status_code == 404

    signup_response = client.post("/activities/Unknown Activity/signup?email=student@mergington.edu")
    assert signup_response.status_code == 404

    unregister_response = client.delete("/activities/Unknown Activity/unregister?email=student@mergington.edu")
    assert unregister_response.status_code == 404
