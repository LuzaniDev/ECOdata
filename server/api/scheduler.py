from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from server.core.audit import add_audit
from server.core.database import Schedule, get_session
from server.core.scheduler_core import exportar_windows_task_scheduler

router = APIRouter(prefix="/api/scheduler", tags=["Scheduler"])


class ScheduleCreate(BaseModel):
    name: str
    tipo: str
    cron_expression: str | None = None
    interval_minutes: int | None = None
    enabled: bool = True
    send_sftp: bool = True


class ScheduleUpdate(BaseModel):
    name: str | None = None
    tipo: str | None = None
    cron_expression: str | None = None
    interval_minutes: int | None = None
    enabled: bool | None = None
    send_sftp: bool | None = None


@router.get("")
async def list_schedules(
    search: str = Query(None, description="Filtrar por nome"),
    tipo: str = Query(None, description="Filtrar por tipo"),
    enabled: bool | None = Query(None, description="Filtrar por status"),
):
    session = get_session()
    try:
        q = session.query(Schedule)
        if search:
            q = q.filter(Schedule.name.ilike(f"%{search}%"))
        if tipo:
            q = q.filter(Schedule.tipo == tipo.lower())
        if enabled is not None:
            q = q.filter(Schedule.enabled == enabled)
        schedules = q.order_by(Schedule.created_at.desc()).all()
        return [
            {
                "id": s.id,
                "name": s.name,
                "tipo": s.tipo,
                "cron_expression": s.cron_expression,
                "interval_minutes": s.interval_minutes,
                "enabled": s.enabled,
                "send_sftp": s.send_sftp,
                "use_windows_scheduler": s.use_windows_scheduler,
                "last_run": s.last_run.isoformat() if s.last_run else None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in schedules
        ]
    finally:
        session.close()


@router.post("")
async def create_schedule(data: ScheduleCreate):
    session = get_session()
    try:
        s = Schedule(
            name=data.name,
            tipo=data.tipo.lower(),
            cron_expression=data.cron_expression,
            interval_minutes=data.interval_minutes,
            enabled=data.enabled,
            send_sftp=data.send_sftp,
        )
        session.add(s)
        session.commit()
        session.refresh(s)
        add_audit(
            user_id=None, username="api",
            action="create", resource_type="schedule",
            resource_id=str(s.id), new_value=data.name,
        )
        return {"id": s.id, "message": "Schedule created"}
    finally:
        session.close()


@router.put("/{schedule_id}")
async def update_schedule(schedule_id: int, data: ScheduleUpdate):
    session = get_session()
    try:
        s = session.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not s:
            raise HTTPException(404, "Schedule not found")

        old_name = s.name
        if data.name is not None:
            s.name = data.name
        if data.tipo is not None:
            s.tipo = data.tipo.lower()
        if data.cron_expression is not None:
            s.cron_expression = data.cron_expression
        if data.interval_minutes is not None:
            s.interval_minutes = data.interval_minutes
        if data.enabled is not None:
            s.enabled = data.enabled
        if data.send_sftp is not None:
            s.send_sftp = data.send_sftp
        s.updated_at = datetime.now()

        session.commit()
        add_audit(
            user_id=None, username="api",
            action="update", resource_type="schedule",
            resource_id=str(schedule_id),
            old_value=old_name, new_value=s.name,
        )
        return {"message": "Schedule updated"}
    finally:
        session.close()


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: int):
    session = get_session()
    try:
        s = session.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not s:
            raise HTTPException(404, "Schedule not found")
        name = s.name
        session.delete(s)
        session.commit()
        add_audit(
            user_id=None, username="api",
            action="delete", resource_type="schedule",
            resource_id=str(schedule_id), old_value=name,
        )
        return {"message": "Schedule deleted"}
    finally:
        session.close()


@router.post("/{schedule_id}/toggle")
async def toggle_schedule(schedule_id: int):
    session = get_session()
    try:
        s = session.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not s:
            raise HTTPException(404, "Schedule not found")
        s.enabled = not s.enabled
        s.updated_at = datetime.now()
        session.commit()
        add_audit(
            user_id=None, username="api",
            action="toggle", resource_type="schedule",
            resource_id=str(schedule_id),
            new_value="enabled" if s.enabled else "disabled",
        )
        return {"enabled": s.enabled, "message": "Schedule toggled"}
    finally:
        session.close()


@router.post("/{schedule_id}/run")
async def run_schedule_now(schedule_id: int, empresa: str = Query(None, description="Empresa para executar (opcional)")):
    session = get_session()
    try:
        s = session.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not s:
            raise HTTPException(404, "Schedule not found")
        from server.core.auditoria import registrar_execucao
        from server.core.executor import run_generator

        result = run_generator(s.tipo, empresa=empresa, send_sftp=s.send_sftp)
        registrar_execucao(result)
        return {"status": result["status"], "message": "Execution completed", "result": result}
    finally:
        session.close()


@router.post("/{schedule_id}/export-windows")
async def export_windows(schedule_id: int):
    result = exportar_windows_task_scheduler(schedule_id)
    if not result["success"]:
        raise HTTPException(400, result.get("error", "Export failed"))
    return result


@router.post("/run-tipo")
async def run_tipo_direto(
    tipo: str = Query(..., description="Tipo: sellout, estoque, painel, todos"),
    empresa: str = Query(None, description="Codigo da empresa (opcional)"),
    send_sftp: bool = Query(False, description="Enviar via SFTP"),
):
    from server.core.auditoria import registrar_execucao
    from server.core.executor import run_generator

    result = run_generator(tipo, empresa=empresa, send_sftp=send_sftp, primeiro_envio=True)
    registrar_execucao(result)
    return {"status": result["status"], "message": "Execution completed", "result": result}