from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from oauth2 import get_current_user
import models

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

        blogs_count = db.execute(text("SELECT COUNT(*) FROM blogs")).scalar()

        return {
            "fk_constraints_to_time_blocks": [
                {"table": r[0], "column": r[1], "constraint": r[2]} for r in fk_info
            ],
            "blogs_row_count": blogs_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-all-data")  # ✅ THÊM DECORATOR
def clear_all_data(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        uid = current_user.id

        # Lấy period_ids của user
        period_ids = db.execute(
            text("SELECT id FROM periods WHERE user_id = :uid"),
            {"uid": uid}
        ).scalars().all()

        if not period_ids:
            return {"message": "Không có dữ liệu để xóa", "user_id": uid}

        # Lấy block_ids từ database
        block_ids = db.execute(
            text("SELECT id FROM time_blocks WHERE period_id IN (:period_ids)"),
            {"period_ids": tuple(period_ids)}
        ).scalars().all()

        if block_ids:
            # ✅ XÓA BẢNG PHỤ THUỘC TRƯỚC (quan trọng!)
            # Xóa theo thứ tự: bảng con → bảng cha
            db.execute(
                text("DELETE FROM blogs WHERE block_id IN (:block_ids)"),
                {"block_ids": tuple(block_ids)}
            )
            db.execute(
                text("DELETE FROM predicts WHERE block_id IN (:block_ids)"),
                {"block_ids": tuple(block_ids)}
            )
            db.execute(
                text("DELETE FROM sensor_data WHERE block_id IN (:block_ids)"),
                {"block_ids": tuple(block_ids)}
            )
            db.execute(
                text("DELETE FROM prediction_data WHERE block_id IN (:block_ids)"),
                {"block_ids": tuple(block_ids)}
            )
            db.execute(
                text("DELETE FROM prediction_raw_data WHERE block_id IN (:block_ids)"),
                {"block_ids": tuple(block_ids)}
            )

            # ✅ XÓA BẢNG CHÍNH CUỐI CÙNG
            db.execute(
                text("DELETE FROM time_blocks WHERE id IN (:block_ids)"),
                {"block_ids": tuple(block_ids)}
            )

        # Xóa periods cuối cùng
        db.execute(
            text("DELETE FROM periods WHERE user_id = :uid"),
            {"uid": uid}
        )

        db.commit()
        return {
            "message": "Đã xóa toàn bộ dữ liệu",
            "user_id": uid,
            "deleted_periods": len(period_ids),
            "deleted_blocks": len(block_ids)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )
