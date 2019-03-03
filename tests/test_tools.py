from flask import url_for


def test_valid_form_is_entered(client):
    data = {"post_to_post": "1500", "spacing": "100", "bar_size": "12"}
    response = client.post(
        url_for("tools.bar_spacer"), data=data, follow_redirects=True
    )

    assert b"Actual gap : <strong>96.0</strong>" in response.data


def test_non_valid_form_is_entered(client):
    data = {"post_to_post": "1500", "spacing": "100", "bar_size": "four"}
    response = client.post(
        url_for("tools.bar_spacer"), data=data, follow_redirects=True
    )

    assert b"input needs to be a number" in response.data


def test_non_valid_form_is_entered_for_louver(client):
    data = {"height": "450", "width": "None"}
    response = client.post(
        url_for("tools.louver_calculator"), data=data, follow_redirects=True
    )

    assert b"input needs to be a number" in response.data
