import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    # Snapshot activities and restore after each test to keep tests isolated
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(orig)


def test_get_activities():
    with TestClient(app) as client:
        resp = client.get("/activities")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "Basketball" in data


def test_signup_and_duplicate():
    activity = "Basketball"
    email = "testuser@example.com"
    with TestClient(app) as client:
        # Signup should succeed
        resp = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert resp.status_code == 200
        assert email in activities[activity]["participants"]

        # Duplicate signup should fail
        resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert resp2.status_code == 400


def test_unregister():
    activity = "Basketball"
    email = "to_remove@example.com"
    with TestClient(app) as client:
        # First sign up
        resp = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert resp.status_code == 200
        assert email in activities[activity]["participants"]

        # Now unregister
        resp2 = client.post(f"/activities/{activity}/unregister", params={"email": email})
        assert resp2.status_code == 200
        assert email not in activities[activity]["participants"]

        # Unregistering again should fail
        resp3 = client.post(f"/activities/{activity}/unregister", params={"email": email})
        assert resp3.status_code == 400
