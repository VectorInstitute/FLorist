import json

from florist.api import client


def test_connect():
    response = client.connect()

    assert response.status_code == 200
    assert response.body.decode() == json.dumps({"status": "ok"}, separators=(",", ":"))
