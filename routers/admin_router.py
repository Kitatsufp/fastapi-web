from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from oauth2 import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.delete("/clear-all")
def clear_all_data(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Xóa toàn bộ dữ liệu sensor/prediction của user hiện tại.
    Xóa theo đúng thứ tự để tránh foreign key constraint.
    """
    # Xóa data tables trước (có FK trỏ về sensor_time_blocks)
    db.execute(text("""
        DELETE FROM sensor_data
        WHERE block_id IN (
            SELECT stb.id FROM sensor_time_blocks stb
            JOIN periods p ON stb.period_id = p.id
            WHERE p.user_id = :uid
        )
    """), {"uid": current_user.id})

    db.execute(text("""
        DELETE FROM prediction_data
        WHERE block_id IN (
            SELECT stb.id FROM sensor_time_blocks stb
            JOIN periods p ON stb.period_id = p.id
            WHERE p.user_id = :uid
        )
    """), {"uid": current_user.id})

    db.execute(text("""
        DELETE FROM prediction_raw_data
        WHERE block_id IN (
            SELECT stb.id FROM sensor_time_blocks stb
            JOIN periods p ON stb.period_id = p.id
            WHERE p.user_id = :uid
        )
    """), {"uid": current_user.id})

    # Xóa sensor_time_blocks
    db.execute(text("""
        DELETE FROM sensor_time_blocks
        WHERE period_id IN (
            SELECT id FROM periods WHERE user_id = :uid
        )
    """), {"uid": current_user.id})

    # Xóa periods
    db.execute(text("""
        DELETE FROM periods WHERE user_id = :uid
    """), {"uid": current_user.id})

    db.commit()

    return {"message": "Đã xóa toàn bộ dữ liệu", "user_id": current_user.id}
