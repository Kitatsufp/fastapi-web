from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from oauth2 import get_current_user
import schemas
from repository import blog
from enums import PeriodEnum, BlockEnum

router = APIRouter(
    prefix="/blog",
    tags=["Blog"]
)


@router.get("/detail")
def get_air_quality_detail(
    period: PeriodEnum,
    block: BlockEnum,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return blog.get_detail(
        user_id=current_user.id,
        period_name=period.value,
        block_name=block.value,
        db=db
    )


@router.post("/")
def create_blog(
    request: schemas.BlogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return blog.create_blog(
        request=request,
        user_id=current_user.id,
        db=db
    )
