from fastapi import APIRouter, Query
from pydantic import BaseModel

from server.core.debug_events import get_events, clear_events, set_paused, is_paused

router = APIRouter(prefix="/api/debug", tags=["Debug"])


@router.get("/pause")
async def get_pause_status():
    return {"paused": is_paused()}


class PauseBody(BaseModel):
    paused: bool


@router.post("/pause")
async def toggle_pause(body: PauseBody):
    set_paused(body.paused)
    return {"paused": body.paused}


@router.get("/events")
async def list_debug_events(
    since_id: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    type: str = Query(None),
):
    return get_events(since_id=since_id, limit=limit, type_filter=type)


@router.post("/events/clear")
async def clear_debug_events():
    clear_events()
    return {"status": "ok"}
