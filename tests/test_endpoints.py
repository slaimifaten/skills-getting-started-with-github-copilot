"""
Integration tests for all API endpoints.

Tests the HTTP endpoints, response codes, and response structure.

Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        ARRANGE: Create client
        ACT: Make GET request to /
        ASSERT: Verify redirect to /static/index.html
        """
        # ARRANGE (client provided by fixture)
        
        # ACT
        response = client.get("/", follow_redirects=False)
        
        # ASSERT
        assert response.status_code == 307, \
            f"Expected redirect status 307, got {response.status_code}"
        assert "/static/index.html" in response.headers["location"], \
            f"Should redirect to /static/index.html, got {response.headers.get('location')}"

    def test_root_with_follow_redirects(self, client):
        """
        ARRANGE: Create client
        ACT: Make GET request to / with redirect following
        ASSERT: Verify final status is 200 and serves HTML
        """
        # ARRANGE (client provided by fixture)
        
        # ACT
        response = client.get("/", follow_redirects=True)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Final response should be 200, got {response.status_code}"
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text, \
            "Should serve HTML content"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities_success(self, client):
        """
        ARRANGE: Create client
        ACT: Make GET request to /activities
        ASSERT: Verify response contains all activities
        """
        # ARRANGE (client provided by fixture)
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Tennis Club", "Drama Club",
            "Art Studio", "Debate Team", "Science Club"
        }
        
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}"
        assert len(data) == 9, \
            f"Expected 9 activities, got {len(data)}"
        assert set(data.keys()) == expected_activities, \
            f"Activities mismatch. Expected {expected_activities}, got {set(data.keys())}"

    def test_activities_have_correct_structure(self, client):
        """
        ARRANGE: Create client and request activities
        ACT: Get activities and inspect structure
        ASSERT: Verify each activity has required fields
        """
        # ARRANGE
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert response.status_code == 200
        for activity_name, activity in data.items():
            assert all(field in activity for field in required_fields), \
                f"Activity '{activity_name}' missing fields. Has: {activity.keys()}"
            assert isinstance(activity["participants"], list), \
                f"Participants in '{activity_name}' should be a list"
            assert isinstance(activity["max_participants"], int), \
                f"max_participants in '{activity_name}' should be an integer"

    def test_activities_participants_are_emails(self, client):
        """
        ARRANGE: Create client and request activities
        ACT: Get activities and check participants
        ASSERT: Verify participants look like emails
        """
        # ARRANGE (client provided by fixture)
        
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        for activity_name, activity in data.items():
            for email in activity["participants"]:
                assert "@" in email, \
                    f"In {activity_name}: '{email}' doesn't look valid"
                assert isinstance(email, str), \
                    f"In {activity_name}: participant should be string"


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """
        ARRANGE: Create client, choose activity and email
        ACT: POST to signup endpoint
        ASSERT: Verify success response
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "newstudent@example.com"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}"
        data = response.json()
        assert "message" in data, \
            "Response should contain message field"
        assert email in data["message"], \
            f"Message should mention email {email}"

    def test_signup_appears_in_activity(self, client):
        """
        ARRANGE: Create client, choose activity and email
        ACT: Signup and then fetch activities
        ASSERT: Verify student appears in activity's participants
        """
        # ARRANGE
        activity_name = "Tennis Club"
        email = "tennis_player@example.com"
        
        # ACT
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # ASSERT
        assert signup_response.status_code == 200
        assert email in activities_data[activity_name]["participants"], \
            f"Student {email} should appear in {activity_name} participants"

    def test_signup_duplicate_prevented(self, client):
        """
        ARRANGE: Create client, choose activity and existing student
        ACT: Try to signup student who's already enrolled
        ASSERT: Verify 400 error is raised
        """
        # ARRANGE
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # ASSERT
        assert response.status_code == 400, \
            f"Expected 400 for duplicate signup, got {response.status_code}"
        data = response.json()
        assert "detail" in data, \
            "Error response should have detail"
        assert "already signed up" in data["detail"].lower(), \
            "Error message should mention duplicate signup"

    def test_signup_nonexistent_activity(self, client):
        """
        ARRANGE: Create client, choose nonexistent activity
        ACT: Try to signup for activity that doesn't exist
        ASSERT: Verify 404 error is raised
        """
        # ARRANGE
        activity_name = "Nonexistent Activity"
        email = "student@example.com"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404, \
            f"Expected 404 for nonexistent activity, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_at_full_capacity(self, client):
        """
        ARRANGE: Create client, find activity at max capacity (fill it first)
        ACT: Try to signup beyond capacity
        ASSERT: Verify 400 error for capacity limit
        """
        # ARRANGE
        activity_name = "Tennis Club"  # max 10, currently has 2
        new_emails = [f"player{i}@example.com" for i in range(8)]  # Fill remaining 8 spots
        
        # Fill the activity to capacity
        for email in new_emails:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        # ACT - Try to signup one more when at capacity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "extra_player@example.com"}
        )
        
        # ASSERT
        assert response.status_code == 400, \
            f"Expected 400 when activity is full, got {response.status_code}"
        data = response.json()
        assert "capacity" in data["detail"].lower(), \
            f"Error should mention capacity: {data['detail']}"


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """
        ARRANGE: Create client, choose activity and enrolled student
        ACT: POST to unregister endpoint
        ASSERT: Verify success response
        """
        # ARRANGE
        activity_name = "Drama Club"
        email = "isabella@mergington.edu"  # enrolled
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}"
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_removes_from_activity(self, client):
        """
        ARRANGE: Create client, enroll student, then unregister
        ACT: Unregister and fetch activities
        ASSERT: Verify student removed from participants
        """
        # ARRANGE
        activity_name = "Art Studio"
        email = "mia@mergington.edu"
        
        # ACT
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # ASSERT
        assert unregister_response.status_code == 200
        assert email not in activities_data[activity_name]["participants"], \
            f"Student {email} should be removed from participants"

    def test_unregister_not_enrolled(self, client):
        """
        ARRANGE: Create client, choose activity and non-enrolled student
        ACT: Try to unregister student not enrolled
        ASSERT: Verify 400 error is raised
        """
        # ARRANGE
        activity_name = "Chess Club"
        not_enrolled_email = "nobody@example.com"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": not_enrolled_email}
        )
        
        # ASSERT
        assert response.status_code == 400, \
            f"Expected 400 for non-enrolled student, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self, client):
        """
        ARRANGE: Create client, choose nonexistent activity
        ACT: Try to unregister from activity that doesn't exist
        ASSERT: Verify 404 error is raised
        """
        # ARRANGE
        activity_name = "Fake Activity"
        email = "student@example.com"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404, \
            f"Expected 404 for nonexistent activity, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_cannot_unregister_twice(self, client):
        """
        ARRANGE: Create client, enroll and unregister student once
        ACT: Try to unregister same student again
        ASSERT: Verify 400 error on second unregister
        """
        # ARRANGE
        activity_name = "Science Club"
        email = "grace@mergington.edu"
        
        # First unregister (should succeed)
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ACT - Try to unregister again
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400, \
            f"Second unregister should fail with 400, got {response.status_code}"
        data = response.json()
        assert "not signed up" in data["detail"].lower()
