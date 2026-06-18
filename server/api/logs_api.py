from fastapi import APIRouter, Query

from server.core.log_core import get_logs

router = APIRouter(prefix="/api/logs", tags=["Logs"])


@router.get("")
async def list_logs(
    limit: int = Query(100, ge=1, le=1000),
    level: str = Query(None, description="Filtrar por nível (INFO, ERROR, WARNING)"),
):
    logs = get_logs(limit=limit, level=level)
    return {"items": logs, "total": len(logs)}