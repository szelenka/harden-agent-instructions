import pytest
from django.test import Client


@pytest.mark.django_db
def test_todo_list_empty():
    client = Client()
    resp = client.get("/todos/")
    assert resp.status_code == 200
    assert resp.json() == []
