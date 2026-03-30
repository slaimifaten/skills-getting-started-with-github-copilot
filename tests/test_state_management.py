"""
Tests for state management and persistence.

Verifies that application state behaves correctly across multiple operations,
and that state resets properly between tests.

Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestStateReset:
    """Test that state is properly reset between tests."""

    def test_initial_chess_club_participants(self, client):
        """
        ARRANGE: Create client
        ACT: Fetch activities
        ASSERT: Verify Chess Club has initial state (2 members)
        """
        # ARRANGE (client from fixture)
        
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        chess_participants = activities["Chess Club"]["participants"]
        assert len(chess_participants) == 2, \
            f"Chess Club should start with 2 participants, has {len(chess_participants)}"
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants

    def test_state_reset_after_signup(self, client):
        """
        ARRANGE: Create two requests - first to signup, second to verify state
        ACT: Signup in first request, then get activities in second
        ASSERT: Second request should see the signup reflected
        """
        # ARRANGE
        activity_name = "Basketball Team"
        email = "new_player@example.com"
        
        # ACT
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # ASSERT
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"], \
            "State should be maintained within a test"


class TestStateConsistency:
    """Test that state remains consistent across operations."""

    def test_multiple_signups_independent(self, client):
        """
        ARRANGE: Prepare multiple different students and activities
        ACT: Sign them all up to different activities
        ASSERT: Verify each signup worked independently
        """
        # ARRANGE
        operations = [
            ("Chess Club", "alice@example.com"),
            ("Drama Club", "bob@example.com"),
            ("Science Club", "charlie@example.com"),
        ]
        
        # ACT
        for activity_name, email in operations:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200, \
                f"Signup failed for {email} in {activity_name}"
        
        # ASSERT - Verify all are in their respective activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        for activity_name, email in operations:
            assert email in activities[activity_name]["participants"], \
                f"{email} should be in {activity_name}"

    def test_signup_then_unregister_sequence(self, client):
        """
        ARRANGE: Choose activity and email
        ACT: Sign up, verify enrolled, unregister, verify removed
        ASSERT: State changes correctly at each step
        """
        # ARRANGE
        activity_name = "Debate Team"
        email = "debater@example.com"
        
        # ACT - Step 1: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # ACT - Step 2: Verify enrolled
        activities1 = client.get("/activities").json()
        assert email in activities1[activity_name]["participants"], \
            f"After signup, {email} should be enrolled"
        
        # ACT - Step 3: Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # ASSERT - Step 4: Verify unregistered
        activities2 = client.get("/activities").json()
        assert email not in activities2[activity_name]["participants"], \
            f"After unregister, {email} should not be enrolled"

    def test_other_participants_unaffected_by_unregister(self, client):
        """
        ARRANGE: Get original participant count, add new student, unregister original
        ACT: Unregister one participant
        ASSERT: Verify other participants remain unchanged
        """
        # ARRANGE
        activity_name = "Art Studio"
        original_activities = client.get("/activities").json()
        original_participants = original_activities[activity_name]["participants"].copy()
        student_to_remove = original_participants[0]
        other_student = original_participants[1]
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": student_to_remove}
        )
        updated_activities = client.get("/activities").json()
        updated_participants = updated_activities[activity_name]["participants"]
        
        # ASSERT
        assert response.status_code == 200
        assert student_to_remove not in updated_participants, \
            "Removed student should not be in list"
        assert other_student in updated_participants, \
            "Other students should remain in list"
        assert len(updated_participants) == len(original_participants) - 1, \
            "Participant count should decrease by 1"


class TestCapacityStateManagement:
    """Test state management related to activity capacity."""

    def test_capacity_decrements_correctly(self, client):
        """
        ARRANGE: Get activity and initial available spaces
        ACT: Sign up multiple students
        ASSERT: Verify available spaces decrease
        """
        # ARRANGE
        activity_name = "Basketball Team"
        original_activities = client.get("/activities").json()
        max_capacity = original_activities[activity_name]["max_participants"]
        original_count = len(original_activities[activity_name]["participants"])
        original_available = max_capacity - original_count
        
        # ACT - Add one student
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "new_player@example.com"}
        )
        
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity_name]["participants"])
        updated_available = max_capacity - updated_count
        
        # ASSERT
        assert response.status_code == 200
        assert updated_count == original_count + 1, \
            "Participant count should increase by 1"
        assert updated_available == original_available - 1, \
            "Available spots should decrease by 1"

    def test_cannot_exceed_capacity_in_sequence(self, client):
        """
        ARRANGE: Find small activity, fill it completely
        ACT: Try to signup beyond capacity
        ASSERT: Final student signup should fail
        """
        # ARRANGE
        activity_name = "Tennis Club"  # max 10
        original_activities = client.get("/activities").json()
        max_capacity = original_activities[activity_name]["max_participants"]
        current_count = len(original_activities[activity_name]["participants"])
        remaining_spots = max_capacity - current_count
        
        # Fill remaining spots
        for i in range(remaining_spots):
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"filler{i}@example.com"}
            )
            assert response.status_code == 200, \
                f"Should be able to fill spot {i}"
        
        # ACT - Try to go beyond capacity
        overflow_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@example.com"}
        )
        
        # ASSERT
        assert overflow_response.status_code == 400, \
            "Should not allow signup beyond capacity"
        final_activities = client.get("/activities").json()
        final_count = len(final_activities[activity_name]["participants"])
        assert final_count == max_capacity, \
            f"Activity should have exactly {max_capacity} participants"


class TestParticipantIsolation:
    """Test that changes to one activity don't affect others."""

    def test_signup_one_activity_not_affects_others(self, client):
        """
        ARRANGE: Get initial state of multiple activities
        ACT: Sign up to one activity
        ASSERT: Verify other activities unchanged
        """
        # ARRANGE
        initial_activities = client.get("/activities").json()
        initial_chess = initial_activities["Chess Club"]["participants"].copy()
        initial_drama = initial_activities["Drama Club"]["participants"].copy()
        
        # ACT - Sign up to Programming Class
        client.post(
            f"/activities/Programming Class/signup",
            params={"email": "programmer@example.com"}
        )
        
        # ASSERT - Check other activities unchanged
        updated_activities = client.get("/activities").json()
        assert updated_activities["Chess Club"]["participants"] == initial_chess, \
            "Unrelated activity (Chess Club) should not change"
        assert updated_activities["Drama Club"]["participants"] == initial_drama, \
            "Unrelated activity (Drama Club) should not change"

    def test_unregister_one_activity_not_affects_others(self, client):
        """
        ARRANGE: Get initial state of multiple activities
        ACT: Unregister from one activity
        ASSERT: Verify other activities unchanged
        """
        # ARRANGE
        initial_activities = client.get("/activities").json()
        initial_science = initial_activities["Science Club"]["participants"].copy()
        initial_prog = initial_activities["Programming Class"]["participants"].copy()
        
        # ACT - Unregister from Gym Class
        client.post(
            f"/activities/Gym Class/unregister",
            params={"email": "john@mergington.edu"}  # in Gym Class
        )
        
        # ASSERT - Check other activities unchanged
        updated_activities = client.get("/activities").json()
        assert updated_activities["Science Club"]["participants"] == initial_science, \
            "Unrelated activity (Science Club) should not change"
        assert updated_activities["Programming Class"]["participants"] == initial_prog, \
            "Unrelated activity (Programming Class) should not change"
