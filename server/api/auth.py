from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from server.core.database import User, get_session, hash_api_key, verify_api_key

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def get_current_user(authorization: str = Header(None), session: Session = Depends(get_session)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token nao fornecido")
    api_key = authorization.split(" ", 1)[1]
    user = session.query(User).filter(User.is_active == True).all()
    for u in user:
        if verify_api_key(api_key, u.api_key_hash):
            return u
    raise HTTPException(status_code=401, detail="Token invalido")


@router.get("/verify")
async def verify_auth(user: User = Depends(get_current_user)):
    return {"authenticated": True, "username": user.username, "role": user.role}
