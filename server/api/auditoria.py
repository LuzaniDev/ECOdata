from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from server.core.audit import add_audit
from server.core.database import Execution, get_session

router = APIRouter(prefix="/api/auditoria", tags=["Auditoria"])


@router.get("")
async def get_execucoes(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    tipo: str = None,
    status: str = None,
):
    session = get_session()
    try:
        q = session.query(Execution)
        if tipo:
            q = q.filter(Execution.tipo == tipo.lower())
        if status:
            q = q.filter(Execution.status == status)
        total = q.count()
        q = q.order_by(Execution.started_at.desc())
        q = q.offset((page - 1) * per_page).limit(per_page)
        items = q.all()
        return {
            "items": [
                {
                    "id": e.id,
                    "tipo": e.tipo,
                    "status": e.status,
                    "started_at": e.started_at.isoformat() if e.started_at else None,
                    "finished_at": e.finished_at.isoformat() if e.finished_at else None,
                    "duration_ms": e.duration_ms,
                    "file_path": e.file_path,
                    "file_hash": e.file_hash,
                    "rows_count": e.rows_count,
                    "file_size": e.file_size,
                    "error_message": e.error_message,
                }
                for e in items
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    finally:
        session.close()


@router.get("/{exec_id}")
async def get_execucao(exec_id: int):
    session = get_session()
    try:
        e = session.query(Execution).filter(Execution.id == exec_id).first()
        if not e:
            raise HTTPException(404, "Execution not found")
        return {
            "id": e.id,
            "tipo": e.tipo,
            "status": e.status,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "finished_at": e.finished_at.isoformat() if e.finished_at else None,
            "duration_ms": e.duration_ms,
            "file_path": e.file_path,
            "file_hash": e.file_hash,
            "rows_count": e.rows_count,
            "file_size": e.file_size,
            "error_message": e.error_message,
            "output_log": e.output_log,
            "created_by": e.created_by,
        }
    finally:
        session.close()


@router.post("/{exec_id}/cancel")
async def cancel_execucao(exec_id: int):
    session = get_session()
    try:
        e = session.query(Execution).filter(Execution.id == exec_id).first()
        if not e:
            raise HTTPException(404, "Execution not found")
        if e.status not in ("running", "pending"):
            raise HTTPException(400, f"Execution status is '{e.status}', cannot cancel")
        e.status = "cancelled"
        e.finished_at = datetime.now()
        session.commit()
        add_audit(
            user_id=None, username="api",
            action="cancel", resource_type="execution",
            resource_id=str(exec_id),
            new_value="cancelled",
        )
        return {"status": "cancelled", "message": "Execution cancelled"}
    finally:
        session.close()


@router.delete("")
async def clean_execucoes(dias: int = Query(90, ge=1)):
    session = get_session()
    try:
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=dias)
        q = session.query(Execution).filter(Execution.started_at < cutoff)
        count = q.delete()
        session.commit()
        add_audit(
            user_id=None, username="api",
            action="clean", resource_type="execution",
            new_value=f"{count} execucoes removidas",
        )
        return {"deleted": count, "message": f"{count} old executions removed"}
    finally:
        session.close()