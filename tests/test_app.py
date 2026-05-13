import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Netflix Clone" in response.data


def test_movie_details_valid(client):
    response = client.get("/movie/1")
    assert response.status_code == 200
    assert b"Inception" in response.data


def test_movie_details_not_found(client):
    response = client.get("/movie/9999")
    assert response.status_code == 404


def test_search_with_results(client):
    response = client.get("/search?q=matrix")
    assert response.status_code == 200
    assert b"Matrix" in response.data


def test_search_empty_query(client):
    response = client.get("/search?q=")
    assert response.status_code == 200
