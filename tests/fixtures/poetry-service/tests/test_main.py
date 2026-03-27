from app.main import app


def test_list_todos():
    client = app.test_client()
    resp = client.get("/todos")
    assert resp.status_code == 200
    assert resp.get_json() == []
