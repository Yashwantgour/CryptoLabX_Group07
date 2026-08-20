def test_search_reflects_untrusted_input():
    from src.app import app

    client = app.test_client()

    payload = "<script>alert('XSS')</script>"

    response = client.get(
        "/search",
        query_string={"q": payload},
    )

    assert response.status_code == 200

    # Intentionally demonstrates the vulnerable behavior:
    # the untrusted input is reflected into the HTML response.
    assert payload.encode() in response.data
