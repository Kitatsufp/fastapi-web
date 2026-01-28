from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import schemas
from repository import user

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)


@router.post("/", response_model=schemas.ShowUser)
def create_user(
    request: schemas.User,
    db: Session = Depends(get_db)
):
    return user.create(request, db)


@router.get("/{id}", response_model=schemas.ShowUser)
def get_user(
    id: int,
    db: Session = Depends(get_db)
):
    return user.show(id, db)
