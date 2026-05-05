from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from oauth2 import get_current_user
import models

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.delete("/clear-all")
def clear_all_data(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Lấy tất cả period_id của user
    period_ids = [p.id for p in db.query(models.Period.id).filter(
        models.Period.user_id == current_user.id
    ).all()]

    if not period_ids:
        return {"message": "Không có dữ liệu để xóa", "user_id": current_user.id}

    # Lấy tất cả block_id thuộc các period đó
    block_ids = [b.id for b in db.query(models.SensorTimeBlock.id).filter(
        models.SensorTimeBlock.period_id.in_(period_ids)
    ).all()]

    if block_ids:
        # Xóa 3 bảng data trước (FK -> sensor_time_blocks)
        db.query(models.SensorData).filter(
            models.SensorData.block_id.in_(block_ids)
        ).delete(synchronize_session=False)

        db.query(models.PredictionData).filter(
            models.PredictionData.block_id.in_(block_ids)
        ).delete(synchronize_session=False)

        db.query(models.PredictionRawData).filter(
            models.PredictionRawData.block_id.in_(block_ids)
        ).delete(synchronize_session=False)

        # Xóa blocks
        db.query(models.SensorTimeBlock).filter(
            models.SensorTimeBlock.period_id.in_(period_ids)
        ).delete(synchronize_session=False)

    # Xóa periods
    db.query(models.Period).filter(
        models.Period.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.commit()

    return {"message": "Đã xóa toàn bộ dữ liệu", "user_id": current_user.id}
