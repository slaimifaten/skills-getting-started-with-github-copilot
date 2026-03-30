"""
Pytest configuration and shared fixtures for the FastAPI Activity Management tests.

Handles setup and teardown of test environment, including state reset between tests.
"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


# Store the original state of activities for reset between tests
ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset the activities dictionary to its original state before each test.
    This ensures tests don't interfere with each other due to in-memory state.
    
    Autouse=True means this runs before every test automatically.
    """
    # Reset activities to original state
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    
    yield
    
    # Cleanup after test (reset again for safety)
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient for making HTTP requests to the application.
    
    ARRANGE phase typically uses this fixture to set up the test client.
    """
    return TestClient(app)
