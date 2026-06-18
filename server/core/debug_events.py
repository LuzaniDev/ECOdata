import time
import traceback
from collections import deque
from datetime import datetime
from threading import Lock

MAX_EVENTS = 2000
_events = deque(maxlen=MAX_EVENTS)
_event_id = 0
_lock = Lock()
_paused = False


_PAUSABLE_TYPES = {"api_request", "api_response"}


def add_event(event_type: str, data: dict, source: str = "system"):
    global _event_id
    with _lock:
        if _paused and event_type in _PAUSABLE_TYPES:
            return _event_id
        _event_id += 1
        _events.append({
            "id": _event_id,
            "type": event_type,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "timestamp_ms": time.time(),
            "data": data,
        })
    return _event_id


def set_paused(paused: bool):
    global _paused
    with _lock:
        _paused = paused
    add_event("system", {"message": "Requisições pausadas" if paused else "Requisições retomadas"}, "sistema")


def is_paused() -> bool:
    return _paused


def get_events(since_id: int = 0, limit: int = 200, type_filter: str = None):
    with _lock:
        result = [e for e in _events if e["id"] > since_id]
    if type_filter:
        result = [e for e in result if e["type"] == type_filter]
    result = result[-limit:]
    last_id = _event_id
    return {"events": result, "total": len(result), "last_id": last_id}


def clear_events():
    global _event_id
    with _lock:
        _events.clear()
        _event_id = 0
