from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/config", tags=["Test Connection"])


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
