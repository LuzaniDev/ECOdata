import os
import subprocess
import sys
import threading
from datetime import datetime

from server.core.auditoria import registrar_execucao
from server.core.database import Schedule, get_session
from server.core.debug_events import add_event
from server.core.executor import run_generator
from server.core.log_core import add_log

POLL_INTERVAL = int(os.getenv("SCHEDULER_POLL_INTERVAL", "30"))
scheduler_thread = None
stop_event = threading.Event()
schedule_locks = {}
_cron_ultimo_disparo = {}
_running_tasks: dict[int, threading.Thread] = {}
_running_tasks_lock = threading.Lock()


def executar_tarefa(schedule_id: int):
    session = get_session()
    try:
        sched = session.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not sched or not sched.enabled:
            return
        tipo = sched.tipo
        send_sftp = sched.send_sftp
    finally:
        session.close()

    add_event("scheduler_cycle", {"action": "executar_tarefa", "schedule_id": schedule_id, "tipo": tipo}, "scheduler")
    result = run_generator(tipo, send_sftp=send_sftp)
    registrar_execucao(result)


def _campo_cron_corresponde(expr, valor, min_val, max_val):
    if expr == "*" or expr == "*/1":
        return True
    for parte in expr.split(","):
        parte = parte.strip()
        if not parte:
            continue
        if parte.startswith("*/"):
            passo = int(parte[2:])
            if valor % passo == 0:
                return True
        elif "-" in parte:
            a, b = parte.split("-", 1)
            if int(a) <= valor <= int(b):
                return True
        else:
            if int(parte) == valor:
                return True
    return False


_DOW_NAMES = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
_DOW_PARA_CRON = [1, 2, 3, 4, 5, 6, 0]


def _normalizar_dow_expr(expr):
    expr = expr.lower()
    for nome in _DOW_NAMES:
        idx = str(_DOW_NAMES.index(nome))
        expr = expr.replace(nome, idx)
    return expr


def _cron_corresponde(expr, dt):
    parts = expr.strip().split()
    if len(parts) != 5:
        return False
    min_expr, hour_expr, day_expr, month_expr, dow_expr = parts
    if not _campo_cron_corresponde(min_expr, dt.minute, 0, 59):
        return False
    if not _campo_cron_corresponde(hour_expr, dt.hour, 0, 23):
        return False
    if not _campo_cron_corresponde(day_expr, dt.day, 1, 31):
        return False
    if not _campo_cron_corresponde(month_expr, dt.month, 1, 12):
        return False
    dt_dow = _DOW_PARA_CRON[dt.weekday()]
    return _campo_cron_corresponde(_normalizar_dow_expr(dow_expr), dt_dow, 0, 6)


def _deve_executar(s, now):
    if not s.enabled:
        return False
    if s.interval_minutes:
        if s.last_run is None:
            return True
        elapsed = (now - s.last_run).total_seconds()
        return elapsed >= s.interval_minutes * 60
    if s.cron_expression:
        if not _cron_corresponde(s.cron_expression, now):
            return False
        chave = now.strftime("%Y%m%d%H%M")
        if _cron_ultimo_disparo.get(s.id) == chave:
            return False
        _cron_ultimo_disparo[s.id] = chave
        return True
    return False


def _atualizar_last_run(schedule_id):
    session = get_session()
    try:
        s = session.query(Schedule).filter(Schedule.id == schedule_id).first()
        if s:
            s.last_run = datetime.now()
            session.commit()
    except Exception as e:
        add_log("ERROR", f"Erro ao atualizar last_run: {e}", "scheduler")
    finally:
        session.close()


def _run_schedule_task(schedule_id: int, tipo: str, send_sftp: bool):
    try:
        result = run_generator(tipo, send_sftp=send_sftp)
        registrar_execucao(result)
        _atualizar_last_run(schedule_id)
    except Exception as e:
        add_log("ERROR", f"Agendador: falha na execucao do schedule {schedule_id}: {e}", "scheduler")
        try:
            result = {
                "tipo": tipo,
                "status": "failed",
                "started_at": datetime.now(),
                "finished_at": datetime.now(),
                "duration_ms": 0,
                "error_message": str(e),
                "output_log": "",
            }
            registrar_execucao(result)
        except Exception:
            pass
    finally:
        with _running_tasks_lock:
            _running_tasks.pop(schedule_id, None)


def _polling_loop():
    add_log("INFO", "Agendador: polling loop iniciado", "scheduler")
    add_event("scheduler_cycle", {"action": "polling_iniciado"}, "scheduler")
    while not stop_event.is_set():
        try:
            session = get_session()
            try:
                schedules = session.query(Schedule).filter(Schedule.enabled).all()
            finally:
                session.close()

            agora = datetime.now()
            add_event("scheduler_cycle", {"action": "polling_cycle", "checked": len(schedules)}, "scheduler")
            for s in schedules:
                try:
                    if not _deve_executar(s, agora):
                        continue

                    lock = schedule_locks.setdefault(s.id, threading.Lock())
                    if not lock.acquire(blocking=False):
                        continue

                    try:
                        add_log("INFO", f"Agendador: executando schedule {s.id} ({s.tipo})", "scheduler")
                        add_event("scheduler_cycle", {"action": "executando", "schedule_id": s.id, "tipo": s.tipo}, "scheduler")
                        task_thread = threading.Thread(
                            target=_run_schedule_task, args=(s.id, s.tipo, s.send_sftp), daemon=True
                        )
                        with _running_tasks_lock:
                            _running_tasks[s.id] = task_thread
                        task_thread.start()
                    except Exception as e:
                        add_log("ERROR", f"Agendador: falha ao iniciar schedule {s.id}: {e}", "scheduler")
                        add_event("error", {"message": str(e), "context": f"start_schedule_{s.id}"}, "scheduler")
                    finally:
                        lock.release()
                except Exception as e:
                    add_log("ERROR", f"Agendador: erro ao processar schedule {s.id}: {e}", "scheduler")
                    add_event("error", {"message": str(e), "context": f"process_schedule_{s.id}"}, "scheduler")
        except Exception as e:
            add_log("ERROR", f"Agendador: erro no ciclo de polling: {e}", "scheduler")
            add_event("error", {"message": str(e), "context": "polling_cycle"}, "scheduler")

        stop_event.wait(POLL_INTERVAL)

    add_log("INFO", "Agendador: polling loop encerrado", "scheduler")
    add_event("scheduler_cycle", {"action": "polling_finalizado"}, "scheduler")


def init_scheduler():
    global scheduler_thread
    stop_event.clear()
    scheduler_thread = threading.Thread(target=_polling_loop, daemon=True)
    scheduler_thread.start()
    add_log("INFO", "Sistema de agendamento iniciado (polling 30s)", "scheduler")


def stop_scheduler():
    stop_event.set()
    if scheduler_thread:
        scheduler_thread.join(timeout=10)

    add_log("INFO", "Aguardando tarefas em execucao...", "scheduler")
    with _running_tasks_lock:
        running = list(_running_tasks.values())
    for t in running:
        t.join(timeout=30)
    add_log("INFO", "Sistema de agendamento parado", "scheduler")


def exportar_windows_task_scheduler(schedule_id: int):
    session = get_session()
    try:
        s = session.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not s:
            return {"success": False, "error": "Schedule not found"}

        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "main.py")
        task_name = f"ECOdata-{s.tipo}-{s.name.replace(' ', '_')}"

        if s.cron_expression:
            parts = s.cron_expression.strip().split()
            if len(parts) == 5:
                minute, hour, day, month, dow = parts
                if dow == "*":
                    dow = "*"
                else:
                    dow_map = {"0": "SUN", "1": "MON", "2": "TUE", "3": "WED", "4": "THU", "5": "FRI", "6": "SAT"}
                    dow = ",".join(dow_map.get(d, d) for d in dow.split(","))

                cmd = (
                    f'schtasks /Create /SC DAILY /TN "{task_name}" '
                    f'/TR "\'{python_exe}\' \'{script_path}\' --tipo {s.tipo}" '
                    f'/ST {hour.zfill(2)}:{minute.zfill(2)} /F'
                )
                if day != "*":
                    cmd = cmd.replace("/SC DAILY", f"/SC MONTHLY /MD {day}")
                if dow != "*":
                    cmd = cmd.replace("/SC DAILY", f"/SC WEEKLY /D {dow}")

                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    s.use_windows_scheduler = True
                    session.commit()
                    return {"success": True, "message": f"Task '{task_name}' created"}
                else:
                    return {"success": False, "error": result.stderr or result.stdout}
        if s.interval_minutes:
            return {"success": False, "error": "Windows Task Scheduler nao suporta intervalos, use CRON"}
    finally:
        session.close()