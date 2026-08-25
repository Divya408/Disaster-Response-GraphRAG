from __future__ import annotations

import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient")


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)


def test_health_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "graph_backend" in data


def test_query_endpoint(client):
    resp = client.post("/api/query", json={"query": "Which shelters can accommodate flood victims from Area A?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "shelter_recommendation"


def test_disaster_analyze_endpoint(client):
    resp = client.post("/api/disaster/analyze", json={"area": "Area A"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["situation"]["area"] == "Area A"


def test_disaster_analyze_unknown_area(client):
    resp = client.post("/api/disaster/analyze", json={"area": "Nonexistent Zone"})
    assert resp.status_code == 404


def test_shelters_endpoint(client):
    resp = client.get("/api/shelters")
    assert resp.status_code == 200
    assert len(resp.json()["shelters"]) > 0


def test_resources_endpoint(client):
    resp = client.get("/api/resources")
    assert resp.status_code == 200
    assert len(resp.json()["resources"]) > 0


def test_hospitals_endpoint(client):
    resp = client.get("/api/hospitals")
    assert resp.status_code == 200
    assert len(resp.json()["hospitals"]) > 0


def test_agencies_endpoint(client):
    resp = client.get("/api/agencies")
    assert resp.status_code == 200
    assert len(resp.json()["agencies"]) > 0


def test_offline_sync_flow(client):
    create_resp = client.post("/api/offline/records", json={"record_type": "assessment", "payload": {"note": "test"}})
    assert create_resp.status_code == 200
    assert create_resp.json()["status"] == "Pending Sync"

    status_resp = client.get("/api/offline/status")
    assert status_resp.json()["pending_sync_count"] >= 1

    sync_resp = client.post("/api/offline/sync")
    assert sync_resp.json()["synced_count"] >= 1


def test_report_generation_endpoint(client):
    resp = client.post("/api/report/generate", json={"area": "Area A"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_graph_endpoint(client):
    resp = client.get("/api/graph")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["nodes"]) > 0
