from sqlalchemy.orm import Session
from datetime import datetime
import models
import schemas
from zoneinfo import ZoneInfo


def get_detail(
    user_id: int,
    period_name: str,
    block_name: str,
    db: Session
):
    rows = (
        db.query(
            models.TimeBlock.time,
            models.Blog.air_quality
        )
        .join(models.Blog, models.Blog.block_id == models.TimeBlock.id)
        .join(models.Period, models.TimeBlock.period_id == models.Period.id)
        .filter(
            models.Period.user_id == user_id,
            models.Period.period_name == period_name,
            models.TimeBlock.block_name == block_name
        )
        .order_by(models.TimeBlock.time)
        .all()
    )

    return [
        {
            "time": time,
            "air_quality": air_quality
        }
        for time, air_quality in rows
    ]


def create_blog(
    request: schemas.BlogCreate,
    user_id: int,
    db: Session
):
    now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    hour = now.hour

    if 5 <= hour < 11:
        period_name = "morning"
    elif 11 <= hour < 16:
        period_name = "afternoon"
    else:
        period_name = "evening"

    if period_name == "morning":
        if 5 <= hour < 7:
            block_name = "early_morning"
        elif 7 <= hour < 9:
            block_name = "mid_morning"
        else:
            block_name = "late_morning"

    elif period_name == "afternoon":
        if 11 <= hour < 13:
            block_name = "early_afternoon"
        elif 13 <= hour < 15:
            block_name = "mid_afternoon"
        else:
            block_name = "late_afternoon"

    else:
        if 16 <= hour < 18:
            block_name = "early_evening"
        elif 18 <= hour < 20:
            block_name = "mid_evening"
        else:
            block_name = "late_evening"

    period = (
        db.query(models.Period)
        .filter(
            models.Period.user_id == user_id,
            models.Period.period_name == period_name
        )
        .first()
    )

    if not period:
        period = models.Period(
            period_name=period_name,
            user_id=user_id
        )
        db.add(period)
        db.commit()
        db.refresh(period)

    block = models.TimeBlock(
        time=now,
        block_name=block_name,
        period_id=period.id
    )
    db.add(block)
    db.commit()
    db.refresh(block)

    blog = models.Blog(
        air_quality=request.air_quality,
        block_id=block.id
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)

    return blog
