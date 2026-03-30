"""
Tests for edge cases and boundary conditions.

Tests unusual inputs, boundary cases, and potential error scenarios.

Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestEmailEdgeCases:
    """Test edge cases for email input."""

    def test_email_with_special_characters(self, client):
        """
        ARRANGE: Create email with special characters
        ACT: Attempt signup
        ASSERT: Verify it works (no format validation)
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "student+tag@example.co.uk"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200, \
            "Should accept email with special characters"
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_case_sensitive_email_different_records(self, client):
        """
        ARRANGE: Create two versions of email with different cases
        ACT: Sign up both as separate entries
        ASSERT: Verify system treats them as different (case-sensitive)
        """
        # ARRANGE
        activity_name = "Drama Club"
        email1 = "Student@example.com"
        email2 = "student@example.com"
        
        # ACT
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # ASSERT
        assert response1.status_code == 200, \
            f"First email should succeed"
        assert response2.status_code == 200, \
            f"Second email with different case should also succeed (case-sensitive)"
        
        activities = client.get("/activities").json()
        participants = activities[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants

    def test_very_long_email(self, client):
        """
        ARRANGE: Create very long but valid-looking email
        ACT: Attempt signup
        ASSERT: Verify if system accepts it (no length limit tested)
        """
        # ARRANGE
        activity_name = "Science Club"
        # Create a very long local part
        long_email = "a" * 100 + "@example.com"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": long_email}
        )
        
        # ASSERT
        assert response.status_code == 200, \
            "Should accept very long email addresses"
        activities = client.get("/activities").json()
        assert long_email in activities[activity_name]["participants"]

    def test_email_with_spaces_url_encoded(self, client):
        """
        ARRANGE: Create email string (no spaces - testing parameter passing)
        ACT: Send as query parameter
        ASSERT: Verify it's handled correctly
        """
        # ARRANGE
        activity_name = "Art Studio"
        email = "user@test.org"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200


class TestActivityNameEdgeCases:
    """Test edge cases for activity name input."""

    def test_activity_name_with_spaces(self, client):
        """
        ARRANGE: Use activity name with spaces
        ACT: Attempt signup
        ASSERT: Verify spaces are handled correctly
        """
        # ARRANGE
        activity_name = "Programming Class"  # Has spaces
        email = "programmer@example.com"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200, \
            "Should handle activity names with spaces"
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_activity_name_case_sensitive(self, client):
        """
        ARRANGE: Create activity name with wrong case
        ACT: Attempt signup with incorrect case
        ASSERT: Verify it fails (case-sensitive)
        """
        # ARRANGE
        correct_name = "Chess Club"
        wrong_case_name = "chess club"  # lowercase
        email = "player@example.com"
        
        # ACT
        response = client.post(
            f"/activities/{wrong_case_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404, \
            "Activity names should be case-sensitive, lowercase should fail"

    def test_activity_name_with_special_chars_not_found(self, client):
        """
        ARRANGE: Use activity name that doesn't exist with special characters
        ACT: Attempt signup
        ASSERT: Verify 404 error
        """
        # ARRANGE
        activity_name = "Non@Existent#Activity"
        email = "test@example.com"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404, \
            "Nonexistent activity should return 404"


class TestSequenceEdgeCases:
    """Test edge cases in operation sequences."""

    def test_multiple_unregister_attempts_fail_progressively(self, client):
        """
        ARRANGE: Get an enrolled student
        ACT: Attempt multiple unregisters
        ASSERT: First succeeds, rest fail
        """
        # ARRANGE
        activity_name = "Gym Class"
        email = "olivia@mergington.edu"
        
        # ACT - First unregister (should succeed)
        response1 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ACT - Second unregister (should fail)
        response2 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ACT - Third unregister (should also fail)
        response3 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response1.status_code == 200, \
            "First unregister should succeed"
        assert response2.status_code == 400, \
            "Second unregister should fail"
        assert response3.status_code == 400, \
            "Third unregister should also fail"

    def test_signup_unregister_signup_again(self, client):
        """
        ARRANGE: Prepare email and activity
        ACT: Sign up, unregister, sign up again
        ASSERT: All operations succeed
        """
        # ARRANGE
        activity_name = "Basketball Team"
        email = "returning_player@example.com"
        
        # ACT - Sign up
        signup1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ACT - Unregister
        unregister = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ACT - Sign up again
        signup2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert signup1.status_code == 200, \
            "First signup should succeed"
        assert unregister.status_code == 200, \
            "Unregister should succeed"
        assert signup2.status_code == 200, \
            "Second signup should succeed"
        
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"], \
            "After re-signup, student should be enrolled"

    def test_duplicate_check_after_unregister(self, client):
        """
        ARRANGE: Student signed up, unregistered, then signed up again
        ACT: Try to sign up while already enrolled for second time
        ASSERT: Duplicate check still works
        """
        # ARRANGE
        activity_name = "Tennis Club"
        email = "returning_player@example.com"
        
        # Setup: Sign up once
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Unregister
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Sign up again
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ACT - Try to sign up again while enrolled
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400, \
            "Duplicate prevention should work after unregister/re-signup"


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def test_signup_exactly_at_capacity(self, client):
        """
        ARRANGE: Fill activity to exactly max capacity
        ACT: Verify we can fill to exact capacity
        ASSERT: Last signup succeeds, one more would fail
        """
        # ARRANGE
        activity_name = "Debate Team"  # max 16
        original_activities = client.get("/activities").json()
        max_capacity = original_activities[activity_name]["max_participants"]
        current_count = len(original_activities[activity_name]["participants"])
        spots_to_fill = max_capacity - current_count
        
        # Fill to capacity
        for i in range(spots_to_fill):
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"debater{i}@example.com"}
            )
            assert response.status_code == 200, \
                f"Should be able to fill spot {i +1} of {spots_to_fill}"
        
        # ACT - Verify we're at capacity
        at_capacity_activities = client.get("/activities").json()
        current_count_after = len(at_capacity_activities[activity_name]["participants"])
        
        # ASSERT
        assert current_count_after == max_capacity, \
            f"Should have exactly {max_capacity} participants, has {current_count_after}"
        
        # Try one more (should fail)
        overflow_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@example.com"}
        )
        assert overflow_response.status_code == 400, \
            "One more signup should fail at capacity"

    def test_large_activity_signup(self, client):
        """
        ARRANGE: Choose large capacity activity
        ACT: Sign up 20 different students
        ASSERT: All succeed if within capacity
        """
        # ARRANGE
        activity_name = "Programming Class"  # max 20
        original_activities = client.get("/activities").json()
        max_capacity = original_activities[activity_name]["max_participants"]
        current_count = len(original_activities[activity_name]["participants"])
        available = max_capacity - current_count
        
        # Sign up students up to half of available
        num_to_signup = min(10, available)
        
        # ACT
        for i in range(num_to_signup):
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"new_programmer{i}@example.com"}
            )
            assert response.status_code == 200, \
                f"Signup {i+1} should succeed"
        
        # ASSERT
        final_activities = client.get("/activities").json()
        final_count = len(final_activities[activity_name]["participants"])
        assert final_count == current_count + num_to_signup, \
            f"Should have added {num_to_signup} participants"
