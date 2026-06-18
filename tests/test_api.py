"""Testes de integracao da API com TestClient e banco temporario."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
tmp_db.close()
os.environ["ECODATA_DB_URL"] = f"sqlite:///{tmp_db.name}"
os.environ["CORS_ORIGINS"] = "http://testserver"

from fastapi.testclient import TestClient

from server.app import app
from server.core.database import User, get_session, hash_api_key, init_db

client = TestClient(app)


@pytest.fixture(autouse=True, scope="session")
def setup_db():
    init_db()
    session = get_session()
    try:
        existing = session.query(User).filter(User.username == "test").first()
        if not existing:
            session.add(User(
                username="test", api_key_hash=hash_api_key("test-key-123"), role="admin", is_active=True,
            ))
            session.commit()
    finally:
        session.close()


class TestHealth:
    def test_health_publico(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["app"] == "ECOdata"

    def test_health_tem_scheduler(self):
        resp = client.get("/api/health")
        assert "scheduler" in resp.json()


class TestAuth:
    def test_sem_token_retorna_401(self):
        resp = client.get("/api/scheduler")
        assert resp.status_code == 401

    def test_token_invalido_retorna_401(self):
        resp = client.get("/api/scheduler", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401

    def test_token_valido_retorna_200(self):
        resp = client.get("/api/scheduler", headers={"Authorization": "Bearer test-key-123"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_verify_endpoint(self):
        resp = client.post("/api/auth/verify", headers={"Authorization": "Bearer test-key-123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is True
        assert data["username"] == "test"


class TestFiles:
    def test_list_files_sem_auth(self):
        resp = client.get("/api/files")
        assert resp.status_code == 401

    def test_list_files_com_auth(self):
        resp = client.get("/api/files", headers={"Authorization": "Bearer test-key-123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data


class TestScheduler:
    def test_list_schedules(self):
        resp = client.get("/api/scheduler?enabled=true", headers={"Authorization": "Bearer test-key-123"})
        assert resp.status_code == 200

    def test_create_schedule(self):
        resp = client.post(
            "/api/scheduler",
            headers={"Authorization": "Bearer test-key-123", "Content-Type": "application/json"},
            json={
                "name": "Teste",
                "tipo": "ESTOQUE",
                "cron_expression": "0 6 * * *",
                "enabled": True,
                "send_sftp": False,
            },
        )
        assert resp.status_code == 200


class TestDashboard:
    def test_kpis(self):
        resp = client.get("/api/dashboard/kpis", headers={"Authorization": "Bearer test-key-123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_execucoes" in data

    def test_status_grafico(self):
        resp = client.get("/api/dashboard/status-grafico", headers={"Authorization": "Bearer test-key-123"})
        assert resp.status_code == 200


class TestLogs:
    def test_list_logs(self):
        resp = client.get("/api/logs", headers={"Authorization": "Bearer test-key-123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data


class TestConfig:
    def test_get_config(self):
        resp = client.get("/api/config", headers={"Authorization": "Bearer test-key-123"})
        assert resp.status_code == 200

    def test_update_config(self):
        resp = client.put(
            "/api/config",
            headers={"Authorization": "Bearer test-key-123", "Content-Type": "application/json"},
            json={"key": "log_retention_days", "value": "90"},
        )
        assert resp.status_code == 200


class TestBackup:
    def test_list_backups(self):
        resp = client.get("/api/backup", headers={"Authorization": "Bearer test-key-123"})
        assert resp.status_code == 200
