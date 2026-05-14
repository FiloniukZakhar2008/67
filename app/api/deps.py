from fastapi import Request, Depends, HTTPException
from jose import jwt
from app.core.security import SECRET_KEY, ALGORITHM


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalid")

    user = await crud_user.get(db, id=int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user