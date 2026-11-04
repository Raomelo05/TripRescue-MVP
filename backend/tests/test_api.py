import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import User
from app.db.session import get_db
from app.security import password_hash
from app.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-only-secret-key-that-is-not-for-production")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)

    def override_get_db():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.state.test_engine = engine
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    del app.state.test_engine
    Base.metadata.drop_all(engine)
    engine.dispose()


def register(client, email="person@example.com"):
    return client.post("/auth/register", json={"email": email, "password": "long-enough-pass"})


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def trip_payload(**updates):
    return {"title": "Ferias", "destination": "Recife", "starts_on": "2026-12-01", "ends_on": "2026-12-04", **updates}


def test_register_normalizes_email_and_login_returns_same_contract(client):
    response = register(client, "  Person@Example.COM ")
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "person@example.com"

    login = client.post("/auth/login", json={"email": "PERSON@example.com", "password": "long-enough-pass"})
    assert login.status_code == 200
    assert login.json()["user"] == body["user"]
    assert login.json()["access_token"] != body["access_token"]

    with Session(client.app.state.test_engine) as db:
        user = db.query(User).one()
        assert user.password_hash != "long-enough-pass"
        assert password_hash.verify("long-enough-pass", user.password_hash)


def test_login_failure_does_not_disclose_account_existence(client):
    register(client)
    known = client.post("/auth/login", json={"email": "person@example.com", "password": "wrong-password"})
    unknown = client.post("/auth/login", json={"email": "missing@example.com", "password": "wrong-password"})
    assert known.status_code == unknown.status_code == 401
    assert known.json() == unknown.json()


def test_trip_validation_and_user_isolation_for_all_operations(client):
    first = register(client, "one@example.com").json()["access_token"]
    second = register(client, "two@example.com").json()["access_token"]
    invalid = client.post("/trips", headers=auth(first), json=trip_payload(starts_on="2026-12-05"))
    assert invalid.status_code == 422

    created = client.post("/trips", headers=auth(first), json=trip_payload())
    assert created.status_code == 201
    trip_id = created.json()["id"]
    assert client.get("/trips", headers=auth(first)).json()[0]["id"] == trip_id
    assert client.get("/trips", headers=auth(second)).json() == []
    for method, payload in (("get", None), ("patch", {"title": "Roubo"}), ("delete", None)):
        response = getattr(client, method)(f"/trips/{trip_id}", headers=auth(second), json=payload) if payload else getattr(client, method)(f"/trips/{trip_id}", headers=auth(second))
        assert response.status_code == 404
    assert client.patch(f"/trips/{trip_id}", headers=auth(first), json={"ends_on": "2026-11-30"}).status_code == 422
    assert client.patch(f"/trips/{trip_id}", headers=auth(first), json={"destination": "Olinda"}).json()["destination"] == "Olinda"
    assert client.delete(f"/trips/{trip_id}", headers=auth(first)).status_code == 204
    assert client.get(f"/trips/{trip_id}", headers=auth(first)).status_code == 404


def test_private_routes_require_valid_token(client):
    assert client.get("/trips").status_code == 401
    assert client.get("/trips", headers=auth("not-a-jwt")).status_code == 401
