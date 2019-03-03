from flask import current_app


def test_app_exists(client):
    assert current_app is not None


def test_app_is_testing(client):
    assert current_app.config["TESTING"]
