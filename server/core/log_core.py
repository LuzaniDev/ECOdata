import os
from datetime import datetime

from server.core.database import LogEntry, get_session


def add_log(level: str, message: str, source: str = "system"):
    session = get_session()
    try:
        log = LogEntry(level=level.upper(), message=message, source=source)
        session.add(log)
        session.commit()
    finally:
        session.close()


def get_logs(limit: int = 100, level: str = None):
    session = get_session()
    try:
        q = session.query(LogEntry)
        if level:
            q = q.filter(LogEntry.level == level.upper())
        q = q.order_by(LogEntry.created_at.desc()).limit(limit)
        return [
            {
                "id": l.id,
                "level": l.level,
                "message": l.message,
                "source": l.source,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in q.all()
        ]
    finally:
        session.close()


def rotate_logs():
    _root = os.getenv("ECODATA_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    logs_dir = os.path.join(_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)


def cleanup_old_logs(days: int = 30):
    session = get_session()
    try:
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        q = session.query(LogEntry).filter(LogEntry.created_at < cutoff)
        count = q.delete()
        session.commit()
        return count
    finally:
        session.close()