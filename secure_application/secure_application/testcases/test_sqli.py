def test_login_page_loads():
    from src.app import app

    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200


def test_invalid_login():
    from src.app import app

    client = app.test_client()

    response = client.post(
        "/",
        data={
            "username": "not-a-real-user",
            "password": "wrong-password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid username" in response.data
