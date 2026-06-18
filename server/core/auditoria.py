import json
from datetime import datetime

from server.core.database import Execution, get_session


def registrar_execucao(result: dict):
    session = get_session()
    try:
        exec_record = Execution(
            tipo=result.get("tipo", "unknown"),
            status=result.get("status", "unknown"),
            started_at=result.get("started_at", datetime.now()),
            finished_at=result.get("finished_at"),
            duration_ms=result.get("duration_ms"),
            file_path=result.get("file_path"),
            file_hash=result.get("file_hash"),
            rows_count=result.get("rows_count", 0),
            file_size=result.get("file_size"),
            error_message=result.get("error_message"),
            output_log=result.get("output_log"),
            created_by="system",
            empresa_utilizada=result.get("empresa_utilizada"),
            empresa_nome=result.get("empresa_nome"),
            available_companies=json.dumps(result["available_companies"], ensure_ascii=False) if result.get("available_companies") else None,
        )
        session.add(exec_record)
        session.commit()
        return exec_record.id
    finally:
        session.close()


def listar_execucoes(page: int = 1, per_page: int = 50, tipo: str = None, status: str = None):
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
                    "empresa_utilizada": e.empresa_utilizada,
                    "empresa_nome": e.empresa_nome,
                    "available_companies": json.loads(e.available_companies) if e.available_companies else None,
                }
                for e in items
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    finally:
        session.close()


def obter_execucao(exec_id: int):
    session = get_session()
    try:
        e = session.query(Execution).filter(Execution.id == exec_id).first()
        if not e:
            return None
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
            "empresa_utilizada": e.empresa_utilizada,
            "empresa_nome": e.empresa_nome,
            "available_companies": json.loads(e.available_companies) if e.available_companies else None,
        }
    finally:
        session.close()


def limpar_execucoes(dias: int = 90):
    session = get_session()
    try:
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=dias)
        q = session.query(Execution).filter(Execution.started_at < cutoff)
        count = q.delete()
        session.commit()
        return count
    finally:
        session.close()