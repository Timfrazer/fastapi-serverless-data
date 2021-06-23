import pytest
import json


def test_get(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_send_valid_json(test_client):
    unicorn_json = {"name": "honey", "rainbow": True}
    response = test_client.post("/unicorn", json=unicorn_json)
    assert response.json() == unicorn_json


def test_send_invalid_json(test_client):
    response = test_client.post("/unicorn", json={})
    assert response.status_code == 422
    assert response.json() =={
            'detail': [{'loc': ['body', 'name'],
             'msg': 'field required',
             'type': 'value_error.missing'},
            {'loc': ['body', 'rainbow'],
             'msg': 'field required',
             'type': 'value_error.missing'}]}

    response = test_client.post("/unicorn", json={"name": "honey", "rainbow": 10})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value could not be parsed to a boolean"