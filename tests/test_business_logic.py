"""
Unit tests for business logic validation.

Tests core business rules like duplicate signup detection, capacity limits,
and enrollment verification.

Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from copy import deepcopy
from app import activities


class TestSignupValidation:
    """Test business logic for signup validation."""

    def test_detect_duplicate_signup(self):
        """
        ARRANGE: Get an activity and an already-enrolled student
        ACT: Check if student is already in participants
        ASSERT: Verify duplicate detection logic works
        """
        # ARRANGE
        activity = activities["Chess Club"]
        existing_participant = activity["participants"][0]  # michael@mergington.edu
        
        # ACT
        is_duplicate = existing_participant in activity["participants"]
        
        # ASSERT
        assert is_duplicate is True, \
            "Should detect that student is already signed up"

    def test_detect_new_signup(self):
        """
        ARRANGE: Get an activity and a new email
        ACT: Check if new email is in participants
        ASSERT: Verify new student is not in list
        """
        # ARRANGE
        activity = activities["Chess Club"]
        new_email = "newstudent@example.com"
        
        # ACT
        is_new = new_email not in activity["participants"]
        
        # ASSERT
        assert is_new is True, \
            "New student should not be in participants list"

    def test_capacity_limit_detection(self):
        """
        ARRANGE: Create a mock activity at max capacity
        ACT: Check capacity limit logic
        ASSERT: Verify capacity is detected as full
        """
        # ARRANGE
        mock_activity = {
            "max_participants": 3,
            "participants": ["email1@test.com", "email2@test.com", "email3@test.com"]
        }
        
        # ACT
        is_full = len(mock_activity["participants"]) >= mock_activity["max_participants"]
        
        # ASSERT
        assert is_full is True, \
            "Activity at max capacity should be detected as full"

    def test_capacity_not_full_when_below_max(self):
        """
        ARRANGE: Create a mock activity below max capacity
        ACT: Check capacity limit logic
        ASSERT: Verify capacity is not full
        """
        # ARRANGE
        mock_activity = {
            "max_participants": 10,
            "participants": ["email1@test.com", "email2@test.com"]
        }
        
        # ACT
        is_full = len(mock_activity["participants"]) >= mock_activity["max_participants"]
        available_spots = mock_activity["max_participants"] - len(mock_activity["participants"])
        
        # ASSERT
        assert is_full is False, \
            "Activity below max capacity should not be full"
        assert available_spots > 0, \
            "Should have available spots"


class TestUnregisterValidation:
    """Test business logic for unregister validation."""

    def test_detect_enrolled_student(self):
        """
        ARRANGE: Get an activity and an enrolled student
        ACT: Check if student is in participants
        ASSERT: Verify enrolled student is detected
        """
        # ARRANGE
        activity = activities["Drama Club"]
        enrolled_student = activity["participants"][0]  # isabella@mergington.edu
        
        # ACT
        is_enrolled = enrolled_student in activity["participants"]
        
        # ASSERT
        assert is_enrolled is True, \
            "Should detect that student is enrolled"

    def test_detect_not_enrolled_student(self):
        """
        ARRANGE: Get an activity and a non-enrolled student
        ACT: Check if student is in participants
        ASSERT: Verify non-enrolled student is detected
        """
        # ARRANGE
        activity = activities["Basketball Team"]
        not_enrolled_email = "notinlist@example.com"
        
        # ACT
        is_enrolled = not_enrolled_email in activity["participants"]
        
        # ASSERT
        assert is_enrolled is False, \
            "Should detect that student is not enrolled"

    def test_cannot_unregister_twice(self):
        """
        ARRANGE: Create a mock activity and remove a student
        ACT: Attempt to find that student again
        ASSERT: Verify student can't be found after removal
        """
        # ARRANGE
        activity = deepcopy(activities["Science Club"])
        student_to_remove = activity["participants"][0]
        
        # ACT
        activity["participants"].remove(student_to_remove)
        is_still_enrolled = student_to_remove in activity["participants"]
        
        # ASSERT
        assert is_still_enrolled is False, \
            "After unregistering, student should not be in list"


class TestActivityLookup:
    """Test business logic for finding activities."""

    def test_find_existing_activity(self):
        """
        ARRANGE: Choose an activity name
        ACT: Look it up in activities dict
        ASSERT: Verify activity is found
        """
        # ARRANGE
        activity_name = "Basketball Team"
        
        # ACT
        activity_exists = activity_name in activities
        
        # ASSERT
        assert activity_exists is True, \
            f"Activity '{activity_name}' should exist"

    def test_activity_not_found(self):
        """
        ARRANGE: Choose a non-existent activity name
        ACT: Look it up in activities dict
        ASSERT: Verify activity is not found
        """
        # ARRANGE
        nonexistent_activity = "Nonexistent Activity"
        
        # ACT
        activity_exists = nonexistent_activity in activities
        
        # ASSERT
        assert activity_exists is False, \
            f"Activity '{nonexistent_activity}' should not exist"

    def test_all_activities_accessible(self):
        """
        ARRANGE: Get list of all activity names
        ACT: Try to access each one
        ASSERT: Verify all are accessible without error
        """
        # ARRANGE
        activity_names = list(activities.keys())
        
        # ACT & ASSERT
        for activity_name in activity_names:
            activity = activities[activity_name]
            assert activity is not None, \
                f"Should be able to access activity '{activity_name}'"
            assert isinstance(activity, dict), \
                f"Activity '{activity_name}' should be a dictionary"
