from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from oauth2 import get_current_user
import schemas
from repository import sensors
from enums import PeriodEnum, BlockEnum
from datetime import date

router = APIRouter(
    prefix="/sensors",
    tags=["Sensors"]
)


@router.get("/detail")
def get_sensor_detail(
    period: PeriodEnum,
    block: BlockEnum,
    metric: str = "iaq",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return sensors.get_detail(
        user_id=current_user.id,
        period_name=period.value,
        block_name=block.value,
        metric=metric,
        db=db
    )


@router.post("/")
def create_sensor_data(
    request: schemas.SensorDataCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return sensors.create_sensor_data(
        request=request,
        user_id=current_user.id,
        db=db
    )


@router.get("/daily")
def get_daily_sensor_data(
    target_date: date,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return sensors.get_daily_data(
        user_id=current_user.id,
        target_date=target_date,
        db=db
    )


@router.get("/all")
def get_all_metrics(
    target_date: date,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return sensors.get_all_metrics_formatted(
        user_id=current_user.id,
        target_date=target_date,
        db=db
    )
