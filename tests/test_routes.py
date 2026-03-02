"""Integration tests for API routes using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestRootRoute:
    """Tests for the GET / root endpoint."""

    def test_root_redirects_to_index_html(self, client):
        """Test that root path redirects to the static index.html file."""
        # Arrange
        # (No setup needed - just using the client fixture)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_with_follow(self, client):
        """Test that following the redirect works."""
        # Arrange
        # (No setup needed)
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == 200


class TestActivitiesListRoute:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities_returns_dict(self, client):
        """Test that GET /activities returns all activities."""
        # Arrange
        # (Activities are pre-loaded by reset_activities fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_includes_details(self, client):
        """Test that activity objects include required fields."""
        # Arrange
        # (Activities fixture provides data)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_participants_empty_initially(self, client):
        """Test that participants list starts empty for all activities."""
        # Arrange
        # (reset_activities fixture ensures empty participants)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert activity_data["participants"] == []


class TestSignupRoute:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_adds_participant_successfully(self, client):
        """Test that a student can successfully sign up for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up for the same activity."""
        # Arrange
        activity_name = "Programming Class"
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        
        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        assert len(participants) == 3
        for email in emails:
            assert email in participants

    def test_signup_duplicate_email_returns_error(self, client):
        """Test that signing up with the same email twice fails."""
        # Arrange
        activity_name = "Drama Club"
        email = "actor@mergington.edu"
        
        # Act - Sign up first time
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Act - Try to sign up again with same email
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_preserves_other_activities(self, client):
        """Test that signing up for one activity doesn't affect others."""
        # Arrange
        activity1 = "Chess Club"
        activity2 = "Basketball Team"
        email = "student@mergington.edu"
        
        # Act - Sign up for Chess Club
        client.post(f"/activities/{activity1}/signup", params={"email": email})
        
        # Assert
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity1]["participants"]
        assert email not in activities[activity2]["participants"]


class TestUnregisterRoute:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_removes_participant_successfully(self, client):
        """Test that a student can successfully unregister from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "student@mergington.edu"
        
        # Sign up first
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Act - Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404."""
        # Arrange
        activity_name = "Ghost Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered_student_returns_400(self, client):
        """Test that unregistering a non-registered student fails."""
        # Arrange
        activity_name = "Programming Class"
        email = "neverregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_one_student_preserves_others(self, client):
        """Test that unregistering one student doesn't affect others."""
        # Arrange
        activity_name = "Gym Class"
        email1 = "alice@mergington.edu"
        email2 = "bob@mergington.edu"
        
        # Sign up both students
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})
        
        # Act - Unregister first student
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email1}
        )
        
        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 not in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_signup_after_unregister(self, client):
        """Test that a student can sign up again after unregistering."""
        # Arrange
        activity_name = "Art Studio"
        email = "artist@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Act - Unregister
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
        
        # Act - Sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestEndToEndScenarios:
    """Integration tests for realistic end-to-end scenarios."""

    def test_full_signup_flow(self, client):
        """Test a complete signup workflow: signup, view, unregister."""
        # Arrange
        activity_name = "Robotics Club"
        email = "inventor@mergington.edu"
        
        # Act 1 - Check initial state
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]
        
        # Act 2 - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Act 3 - Verify signup
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
        
        # Act 4 - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Assert - Final state
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_multiple_students_signup_and_unregister(self, client):
        """Test managing signups and unregistrations for multiple students."""
        # Arrange
        activity_name = "Debate Team"
        emails = ["scholar1@mergington.edu", "scholar2@mergington.edu", "scholar3@mergington.edu"]
        
        # Act - All students sign up
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert - All registered
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert len(participants) == 3
        
        # Act - One student unregisters
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": emails[0]}
        )
        
        # Assert - Two remaining
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert len(participants) == 2
        assert emails[0] not in participants
        assert emails[1] in participants
        assert emails[2] in participants
