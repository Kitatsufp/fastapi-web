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


@router.get("/debug")
def debug_db(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Kiểm tra tất cả bảng có FK trỏ về time_blocks"""
    try:
        # Tìm tất cả FK constraint trỏ về time_blocks
        fk_info = db.execute(text("""
            SELECT
                tc.table_name,
                kcu.column_name,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.referential_constraints rc
                ON tc.constraint_name = rc.constraint_name
            JOIN information_schema.table_constraints tc2
                ON rc.unique_constraint_name = tc2.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc2.table_name = 'time_blocks'
        """)).fetchall()

        # Đếm rows trong blogs
        blogs_count = db.execute(text("SELECT COUNT(*) FROM blogs")).scalar()

        return {
            "fk_constraints_to_time_blocks": [
                {"table": r[0], "column": r[1], "constraint": r[2]} for r in fk_info
            ],
            "blogs_row_count": blogs_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

            # Xóa blogs trước (FK -> time_blocks)
            db.execute(
                text(f"DELETE FROM blogs WHERE block_id IN ({bid_list})"))

            # Xóa 3 bảng data
            db.execute(
                text(f"DELETE FROM sensor_data WHERE block_id IN ({bid_list})"))
            db.execute(
                text(f"DELETE FROM prediction_data WHERE block_id IN ({bid_list})"))
            db.execute(
                text(f"DELETE FROM prediction_raw_data WHERE block_id IN ({bid_list})"))

            # Xóa time_blocks
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
