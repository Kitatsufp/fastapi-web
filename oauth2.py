from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import jwt_token
import models
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db),
    token_str: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = jwt_token.verify_token(token_str, credentials_exception)

    email = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if user is None:
        raise credentials_exception

    return user
