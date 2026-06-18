import os
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/config", tags=["Config"])

ALLOWED_KEYS = {
    "DB_HOST", "DB_PATH", "DB_USER", "DB_PASSWORD",
    "CODIGO_EMPRESA", "CNPJ_DISTRIBUIDOR",
    "SFTP_HOST", "SFTP_PORT", "SFTP_USER", "SFTP_PASSWORD", "SFTP_REMOTE_DIR",
    "ECODATA_PORT",
}


def _env_path() -> Path:
    root = os.getenv("ECODATA_ROOT", Path(__file__).resolve().parents[2])
    return Path(root) / ".env"


@router.get("/env")
async def get_env_config(raw: bool = Query(False)):
    env_path = _env_path()
    if not env_path.exists():
        if raw:
            return "Arquivo .env não encontrado"
        return {}

    if raw:
        return env_path.read_text(encoding="utf-8")

    config = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        config[key.strip()] = val.strip().strip("\"'")

    return {
        "DB_HOST": config.get("DB_HOST", ""),
        "DB_PATH": config.get("DB_PATH", ""),
        "DB_USER": config.get("DB_USER", ""),
        "DB_PASSWORD": config.get("DB_PASSWORD", ""),
        "CODIGO_EMPRESA": config.get("CODIGO_EMPRESA", "01"),
        "CNPJ_DISTRIBUIDOR": config.get("CNPJ_DISTRIBUIDOR", ""),
        "SFTP_HOST": config.get("SFTP_HOST", ""),
        "SFTP_PORT": config.get("SFTP_PORT", "2222"),
        "SFTP_USER": config.get("SFTP_USER", ""),
        "SFTP_PASSWORD": config.get("SFTP_PASSWORD", ""),
        "SFTP_REMOTE_DIR": config.get("SFTP_REMOTE_DIR", "/"),
    }


class EnvUpdate(BaseModel):
    DB_HOST: str = ""
    DB_PATH: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    CODIGO_EMPRESA: str = "01"
    CNPJ_DISTRIBUIDOR: str = ""
    SFTP_HOST: str = ""
    SFTP_PORT: str = "2222"
    SFTP_USER: str = ""
    SFTP_PASSWORD: str = ""
    SFTP_REMOTE_DIR: str = "/"


@router.put("/env")
async def put_env_config(data: EnvUpdate):
    env_path = _env_path()
    existing = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            existing[key.strip()] = val.strip()

    for k, v in data.model_dump().items():
        if k in ALLOWED_KEYS:
            existing[k] = v

    lines = []
    for k, v in existing.items():
        lines.append(f"{k}={v}")
    lines.append("")

    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text("\n".join(lines), encoding="utf-8")
    return {"status": "ok", "message": "Configurações salvas. Reinicie o servidor para aplicar."}


class TestDBReq(BaseModel):
    host: str = ""
    path: str = ""
    user: str = ""
    password: str = ""


@router.post("/test-db")
async def test_db_connection(data: TestDBReq):
    try:
        import fdb
        conn = fdb.connect(
            host=data.host or "localhost",
            database=data.path,
            user=data.user or "SYSDBA",
            password=data.password or "",
            charset="UTF8",
        )
        conn.close()
        return {"status": "ok", "message": "Conexão bem-sucedida"}
    except Exception as e:
        return {"status": "erro", "error": str(e)}


class TestSFTPReq(BaseModel):
    host: str = ""
    port: int = 2222
    user: str = ""
    password: str = ""


@router.post("/test-sftp")
async def test_sftp_connection(data: TestSFTPReq):
    try:
        import paramiko
        transport = paramiko.Transport((data.host, data.port))
        transport.connect(username=data.user, password=data.password)
        transport.close()
        return {"status": "ok", "message": "Conexão SFTP bem-sucedida"}
    except Exception as e:
        return {"status": "erro", "error": str(e)}