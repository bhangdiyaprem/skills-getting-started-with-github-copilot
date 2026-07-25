from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    # Arrange
    endpoint = "/"

    # Act
    response = client.get(endpoint, follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_map(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert f"Signed up {email} for {activity_name}" == response.json()["message"]

    verify_response = client.get("/activities")
    participants = verify_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(endpoint, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_existing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    endpoint = (
        f"/activities/{quote(activity_name, safe='')}/participants/"
        f"{quote(existing_email, safe='')}"
    )

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == (
        f"Unregistered {existing_email} from {activity_name}"
    )

    verify_response = client.get("/activities")
    participants = verify_response.json()[activity_name]["participants"]
    assert existing_email not in participants


def test_unregister_rejects_missing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "not.enrolled@mergington.edu"
    endpoint = (
        f"/activities/{quote(activity_name, safe='')}/participants/"
        f"{quote(missing_email, safe='')}"
    )

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "anyone@mergington.edu"
    endpoint = (
        f"/activities/{quote(activity_name, safe='')}/participants/"
        f"{quote(email, safe='')}"
    )

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
