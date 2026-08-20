def test_authenticated_user_can_request_another_profile():
    from src.app import app

    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "alice"

    response = client.get("/profile/2")

    assert response.status_code == 200

    # Alice should not be able to access Bob's profile.
    # This assertion documents the intentionally vulnerable
    # behavior required for the laboratory.
    assert b"Bob Student" in response.data
