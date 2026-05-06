# sensors_repo.py - PHIÊN BẢN FIXED (Đảm Bảo Xóa Được)

from sqlalchemy.orm import Session
from datetime import datetime, date, time
import models
import schemas
from zoneinfo import ZoneInfo


def get_detail(user_id: int, period_name: str, block_name: str, metric: str, db: Session):
    rows = (db.query(models.SensorTimeBlock.time, models.SensorData)
            .join(models.SensorData, models.SensorData.block_id == models.SensorTimeBlock.id)
            .join(models.Period, models.SensorTimeBlock.period_id == models.Period.id)
            .filter(
            models.Period.user_id == user_id,
            models.Period.period_name == period_name,
            models.SensorTimeBlock.block_name == block_name
            ).order_by(models.SensorTimeBlock.time).all())

    result = []
    for block_time, sensor_data in rows:
        value = getattr(sensor_data, metric, None)
        if value is not None:
            result.append({"time": block_time, "value": value})
    return result


def create_sensor_data(request: schemas.SensorDataCreate, user_id: int, db: Session):
    now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
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

    period = db.query(models.Period).filter(
        models.Period.user_id == user_id,
        models.Period.period_name == period_name
    ).first()

    if not period:
        period = models.Period(period_name=period_name, user_id=user_id)
        db.add(period)
        db.commit()
        db.refresh(period)

    block = models.SensorTimeBlock(
        time=now, block_name=block_name, period_id=period.id)
    db.add(block)
    db.commit()
    db.refresh(block)

    sensor_data = models.SensorData(
        iaq=request.iaq,
        tvoc=request.tvoc,
        eco2=request.eco2,
        etoh=request.etoh,
        block_id=block.id
    )
    db.add(sensor_data)
    db.commit()
    db.refresh(sensor_data)
    return sensor_data


def get_daily_data(user_id: int, target_date: date, db: Session):
    start = datetime.combine(target_date, time.min)
    end = datetime.combine(target_date, time.max)

    rows = (db.query(models.SensorTimeBlock.time, models.SensorData)
            .join(models.SensorData, models.SensorData.block_id == models.SensorTimeBlock.id)
            .join(models.Period, models.SensorTimeBlock.period_id == models.Period.id)
            .filter(
            models.Period.user_id == user_id,
            models.SensorTimeBlock.time >= start,
            models.SensorTimeBlock.time <= end
            ).order_by(models.SensorTimeBlock.time).all())

    return [
        {
            "time": t.strftime("%H:%M:%S"),
            "iaq": sensor_data.iaq,
            "tvoc": sensor_data.tvoc,
            "eco2": sensor_data.eco2,
            "etoh": sensor_data.etoh
        }
        for t, sensor_data in rows
    ]


def get_all_metrics_formatted(user_id: int, target_date: date, db: Session):
    data = get_daily_data(user_id, target_date, db)
    return {
        "iaq": [{"time": item["time"], "value": item["iaq"]} for item in data if item["iaq"] is not None],
        "tvoc": [{"time": item["time"], "value": item["tvoc"]} for item in data if item["tvoc"] is not None],
        "eco2": [{"time": item["time"], "value": item["eco2"]} for item in data if item["eco2"] is not None],
        "etoh": [{"time": item["time"], "value": item["etoh"]} for item in data if item["etoh"] is not None]
    }


def clear_sensor_data(user_id: int, db: Session):
    """
    ✅ FIXED VERSION - Xóa dữ liệu từ trong ra ngoài
    Đảm bảo cascade delete hoạt động đúng
    """
    try:
        # Bước 1: Lấy tất cả periods của user
        periods = db.query(models.Period).filter(
            models.Period.user_id == user_id
        ).all()

        print(f"DEBUG: Found {len(periods)} periods")
        deleted_count = 0

        if not periods:
            return {
                "message": "No sensor data found to clear",
                "deleted_records": 0
            }

        # Bước 2: Loại qua từng period và xóa từng cái
        for period in periods:
            print(f"DEBUG: Processing period {period.id}")

            # Lấy tất cả blocks của period
            blocks = db.query(models.SensorTimeBlock).filter(
                models.SensorTimeBlock.period_id == period.id
            ).all()

            print(f"DEBUG: Found {len(blocks)} blocks in period {period.id}")

            # Xóa từng block (sẽ auto xóa sensor_data nhờ relationship)
            for block in blocks:
                # Xóa SensorData trực tiếp trước
                sensor_data_count = db.query(models.SensorData).filter(
                    models.SensorData.block_id == block.id
                ).delete(synchronize_session=False)

                deleted_count += sensor_data_count
                print(f"DEBUG: Deleted {sensor_data_count} sensor data")

                # Xóa block
                db.delete(block)
                db.flush()  # Flush ngay để chắc chắn xóa

            # Xóa period
            db.delete(period)
            db.flush()  # Flush ngay để chắc chắn xóa

        # IMPORTANT: Commit một lần cuối cùng
        db.commit()
        print(f"DEBUG: Commit successful, deleted {deleted_count} records")

        return {
            "message": "Sensor data cleared successfully",
            "deleted_records": deleted_count
        }

    except Exception as e:
        db.rollback()
        print(f"ERROR: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to clear sensor data"
        }
