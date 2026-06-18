import os

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check():
    try:
        from src.db import get_pool

        pool = get_pool()
        conn = pool.acquire()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM RDB$DATABASE")
        cur.fetchone()
        pool.release(conn)
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {"status": "ok", "database": db_status}


@router.get("/public/api-key")
async def get_api_key():
    api_key_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", ".api_key"
    )
    if os.path.exists(api_key_path):
        for line in open(api_key_path):
            if line.startswith("API Key:"):
                key = line.split(":", 1)[1].strip()
                return {"api_key": key}
    return {"api_key": ""}