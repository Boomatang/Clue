from flask import url_for


def test_valid_form_is_entered(client):
    data = {"post_to_post": "1500",
            "spacing": "100",
            "bar_size": "12"}
    response = client.post(url_for("tools.bar_spacer"),
                           data=data, follow_redirects=True)

    assert b"Actual gap : <strong>96.0</strong>" in response.data
