"""Tests for FLorist's client FastAPI endpoints."""
import json

from florist.api import client


def test_connect() -> None:
    """Tests the client's connect endpoint."""
    response = client.connect()

    assert response.status_code == 200
    assert response.body.decode() == json.dumps({"status": "ok"}, separators=(",", ":"))
