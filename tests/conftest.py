"""Shared pytest fixtures for all tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean state before each test.
    
    This fixture runs automatically before every test (autouse=True)
    to ensure tests don't interfere with each other.
    """
    # Store original activities
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        },
        "Basketball Team": {
            "description": "Compete in basketball games and tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Join our competitive soccer team",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in school plays and performances",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 14,
            "participants": []
        },
        "Debate Team": {
            "description": "Compete in debate tournaments and develop public speaking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": []
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield  # Run the test
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)
