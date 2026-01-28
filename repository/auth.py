from sqlalchemy.orm import Session
from fastapi import HTTPException
import models


def login(request, db: Session):
    user = db.query(models.User).filter(
        models.User.email == request.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Invalid credentials"
        )

    return user
