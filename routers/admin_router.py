from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from oauth2 import get_current_user
import models
import traceback

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.delete("/clear-all")
def clear_all_data(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        uid = current_user.id

        # Lấy period_ids của user
        period_ids = [r[0] for r in db.execute(
            text("SELECT id FROM periods WHERE user_id = :uid"), {"uid": uid}
        ).fetchall()]

        if not period_ids:
            return {"message": "Không có dữ liệu để xóa", "user_id": uid}

        pid_list = ",".join(str(i) for i in period_ids)

        # Lấy block_ids từ bảng thực tế trên DB (time_blocks)
        block_ids = [r[0] for r in db.execute(
            text(f"SELECT id FROM time_blocks WHERE period_id IN ({pid_list})")
        ).fetchall()]

        if block_ids:
            bid_list = ",".join(str(i) for i in block_ids)

            # Xóa 3 bảng data trước
            db.execute(
                text(f"DELETE FROM sensor_data WHERE block_id IN ({bid_list})"))
            db.execute(
                text(f"DELETE FROM prediction_data WHERE block_id IN ({bid_list})"))
            db.execute(
                text(f"DELETE FROM prediction_raw_data WHERE block_id IN ({bid_list})"))

            # Xóa time_blocks (tên thật trên DB)
            db.execute(
                text(f"DELETE FROM time_blocks WHERE id IN ({bid_list})"))

        # Xóa periods
        db.execute(
            text("DELETE FROM periods WHERE user_id = :uid"), {"uid": uid})

        db.commit()
        return {"message": "Đã xóa toàn bộ dữ liệu", "user_id": uid}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"{type(e).__name__}: {str(e)}")
