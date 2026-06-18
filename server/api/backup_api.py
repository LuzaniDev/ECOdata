import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from server.core.database import DB_PATH

router = APIRouter(prefix="/api/backup", tags=["Backup"])


@router.get("/download")
async def download_backup():
    if not os.path.exists(DB_PATH):
        raise HTTPException(404, "Banco de dados não encontrado")

    return FileResponse(DB_PATH, filename="ecodata_backup.db", media_type="application/octet-stream")
