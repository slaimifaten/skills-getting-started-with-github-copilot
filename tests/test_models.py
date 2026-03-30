"""
Unit tests for Activity model structure and validation.

Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from app import activities


class TestActivityStructure:
    """Test the structure and properties of Activity objects."""

    def test_activity_has_required_fields(self):
        """
        ARRANGE: Select first activity from activities
        ACT: Check that required fields exist
        ASSERT: Verify all required fields are present
        """
        # ARRANGE
        activity_name = "Chess Club"
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # ACT
        activity = activities[activity_name]
        
        # ASSERT
        assert all(field in activity for field in required_fields), \
            f"Activity missing required fields. Has: {activity.keys()}, Needs: {required_fields}"

    def test_activity_participants_is_list(self):
        """
        ARRANGE: Get an activity
        ACT: Check participants field type
        ASSERT: Verify it's a list
        """
        # ARRANGE
        activity = activities["Chess Club"]
        
        # ACT & ASSERT
        assert isinstance(activity["participants"], list), \
            "participants field must be a list"

    def test_activity_max_participants_is_integer(self):
        """
        ARRANGE: Get an activity
        ACT: Check max_participants field type
        ASSERT: Verify it's an integer
        """
        # ARRANGE
        activity = activities["Programming Class"]
        
        # ACT & ASSERT
        assert isinstance(activity["max_participants"], int), \
            "max_participants must be an integer"
        assert activity["max_participants"] > 0, \
            "max_participants must be positive"

    def test_all_activities_have_consistent_structure(self):
        """
        ARRANGE: Get all activities
        ACT: Iterate through each activity
        ASSERT: Verify each has consistent structure
        """
        # ARRANGE
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # ACT & ASSERT
        for activity_name, activity in activities.items():
            assert all(field in activity for field in required_fields), \
                f"Activity '{activity_name}' has inconsistent structure"
            assert isinstance(activity["participants"], list), \
                f"Activity '{activity_name}' participants is not a list"
            assert isinstance(activity["max_participants"], int), \
                f"Activity '{activity_name}' max_participants is not an integer"
            assert activity["max_participants"] > 0, \
                f"Activity '{activity_name}' max_participants is not positive"

    def test_activity_initial_participants_are_valid_emails(self):
        """
        ARRANGE: Get all activities and their participants
        ACT: Check each participant
        ASSERT: Verify they appear to be valid emails
        """
        # ARRANGE
        for activity_name, activity in activities.items():
            participants = activity["participants"]
            
            # ACT & ASSERT
            for email in participants:
                assert isinstance(email, str), \
                    f"In {activity_name}: participant is not a string"
                assert "@" in email, \
                    f"In {activity_name}: '{email}' doesn't look like a valid email"

    def test_number_of_activities(self):
        """
        ARRANGE: Count activities
        ACT: Store count
        ASSERT: Verify we have expected number
        """
        # ARRANGE & ACT
        num_activities = len(activities)
        
        # ASSERT
        assert num_activities == 9, \
            f"Expected 9 activities, got {num_activities}"


class TestActivityCapacityLogic:
    """Test capacity-related logic for activities."""

    def test_participants_count_within_capacity(self):
        """
        ARRANGE: Get each activity
        ACT: Count participants
        ASSERT: Verify count doesn't exceed max_participants
        """
        # ARRANGE & ACT & ASSERT
        for activity_name, activity in activities.items():
            num_participants = len(activity["participants"])
            max_capacity = activity["max_participants"]
            
            assert num_participants <= max_capacity, \
                f"{activity_name}: {num_participants} participants exceeds max {max_capacity}"

    def test_activity_can_accept_more_participants(self):
        """
        ARRANGE: Get an activity with available spaces
        ACT: Calculate available spots
        ASSERT: Verify there are spots available for signup
        """
        # ARRANGE
        # Find an activity with available capacity
        activity_name = "Chess Club"  # Currently has 2, max 12
        activity = activities[activity_name]
        
        # ACT
        available_spots = activity["max_participants"] - len(activity["participants"])
        
        # ASSERT
        assert available_spots > 0, \
            f"{activity_name} should have available spots for testing signup"
