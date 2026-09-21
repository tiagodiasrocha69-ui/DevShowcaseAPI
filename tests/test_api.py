import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def make_profile(client, email="tiago@email.com"):
    return client.post("/api/profiles", json={
        "name": "Tiago Silva", "email": email,
        "github_url": "https://github.com/tiago",
    })


def test_create_and_get_profile(client):
    r = make_profile(client)
    assert r.status_code == 201
    pid = r.json()["id"]
    assert client.get(f"/api/profiles/{pid}").json()["name"] == "Tiago Silva"


def test_profile_validations(client):
    assert client.post("/api/profiles", json={"name": "  ", "email": "a@b.com"}).status_code == 422
    assert client.post("/api/profiles", json={"name": "X", "email": "invalido"}).status_code == 422
    assert client.post("/api/profiles", json={
        "name": "X", "email": "a@b.com", "github_url": "nao-e-url"}).status_code == 422


def test_profile_duplicate_email_and_not_found(client):
    make_profile(client)
    assert make_profile(client).status_code == 409
    assert client.get("/api/profiles/999").status_code == 404


def test_technologies(client):
    assert client.post("/api/technologies", json={"name": "Python"}).status_code == 201
    assert client.post("/api/technologies", json={"name": "python"}).status_code == 409
    assert client.post("/api/technologies", json={"name": ""}).status_code == 422
    client.post("/api/technologies", json={"name": "Java"})
    names = [t["name"] for t in client.get("/api/technologies").json()]
    assert names == ["Java", "Python"]


def test_projects(client):
    pid = make_profile(client).json()["id"]
    tid = client.post("/api/technologies", json={"name": "FastAPI"}).json()["id"]

    r = client.post("/api/projects", json={
        "title": "Meu Portfólio", "profile_id": pid, "technology_ids": [tid],
        "repository_url": "https://github.com/tiago/portfolio",
    })
    assert r.status_code == 201
    body = r.json()
    assert body["technologies"][0]["name"] == "FastAPI"
    assert body["feedbacks"] == []

    assert len(client.get("/api/projects").json()) == 1


def test_project_errors(client):
    pid = make_profile(client).json()["id"]
    assert client.post("/api/projects", json={"title": "", "profile_id": pid}).status_code == 422
    assert client.post("/api/projects", json={
        "title": "X", "profile_id": pid, "demo_url": "abc"}).status_code == 422
    assert client.post("/api/projects", json={"title": "X", "profile_id": 999}).status_code == 404
    assert client.post("/api/projects", json={
        "title": "X", "profile_id": pid, "technology_ids": [42]}).status_code == 404
