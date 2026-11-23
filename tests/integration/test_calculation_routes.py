from fastapi.testclient import TestClient

from main import app


def test_calculation_lifecycle():
    with TestClient(app) as client:
        created = client.post(
            "/calculations", json={"a": 10, "b": 5, "type": "Add"}
        )
        assert created.status_code == 201, created.text
        calculation = created.json()
        assert calculation["result"] == 15.0
        url = f"/calculations/{calculation['id']}"

        browse = client.get("/calculations")
        assert browse.status_code == 200
        assert calculation in browse.json()

        read = client.get(url)
        assert read.status_code == 200
        assert read.json() == calculation

        edited = client.put(url, json={"a": 10, "b": 5, "type": "Multiply"})
        assert edited.status_code == 200, edited.text
        assert edited.json() == {**calculation, "type": "Multiply", "result": 50.0}
        assert client.get(url).json() == edited.json()

        deleted = client.delete(url)
        assert deleted.status_code == 204
        assert deleted.content == b""

        missing = client.get(url)
        assert missing.status_code == 404
        assert missing.json()["detail"] == "Calculation not found."
        assert client.delete(url).status_code == 404


def test_calculation_rejects_division_by_zero():
    with TestClient(app) as client:
        response = client.post(
            "/calculations", json={"a": 10, "b": 0, "type": "Divide"}
        )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("Cannot divide by zero." in error["msg"] for error in errors)