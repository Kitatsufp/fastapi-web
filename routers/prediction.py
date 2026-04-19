from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from oauth2 import get_current_user
import schemas
from repository import prediction
import repository.blog as blog_repository
from enums import PeriodEnum, BlockEnum
from datetime import date

router = APIRouter(
    prefix="/Predict",
    tags=["Predict"]
)


@router.get("/detail")
def get_air_quality_detail(
    period: PeriodEnum,
    block: BlockEnum,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return prediction.get_detail(
        user_id=current_user.id,
        period_name=period.value,
        block_name=block.value,
        db=db
    )


@router.post("/")
def create_predict(
    request: schemas.BlogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return prediction.create_predict(
        request=request,
        user_id=current_user.id,
        db=db
    )


@router.get("/daily")
def get_daily(
    target_date: date,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return blog_repository.get_daily_data(
        user_id=current_user.id,
        target_date=target_date,
        db=db
    )
