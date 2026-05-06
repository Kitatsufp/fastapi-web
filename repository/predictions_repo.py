from sqlalchemy.orm import Session
from datetime import datetime, date, time
import models
import schemas
from zoneinfo import ZoneInfo


def get_detail(user_id: int, period_name: str, block_name: str, metric: str, db: Session):
    rows = (db.query(models.SensorTimeBlock.time, models.PredictionData)
            .join(models.PredictionData, models.PredictionData.block_id == models.SensorTimeBlock.id)
            .join(models.Period, models.SensorTimeBlock.period_id == models.Period.id)
            .filter(
            models.Period.user_id == user_id,
            models.Period.period_name == period_name,
            models.SensorTimeBlock.block_name == block_name
            ).order_by(models.SensorTimeBlock.time).all())

    result = []
    for block_time, prediction_data in rows:
        value = getattr(prediction_data, metric, None)
        if value is not None:
            result.append({"time": block_time, "value": value})
    return result


def create_prediction_data(request: schemas.PredictionDataCreate, user_id: int, db: Session):
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

    prediction_data = models.PredictionData(
        iaq=request.iaq,
        tvoc=request.tvoc,
        eco2=request.eco2,
        etoh=request.etoh,
        block_id=block.id
    )
    db.add(prediction_data)
    db.commit()
    db.refresh(prediction_data)
    return prediction_data


def get_daily_data(user_id: int, target_date: date, db: Session):
    start = datetime.combine(target_date, time.min)
    end = datetime.combine(target_date, time.max)

    rows = (db.query(models.SensorTimeBlock.time, models.PredictionData)
            .join(models.PredictionData, models.PredictionData.block_id == models.SensorTimeBlock.id)
            .join(models.Period, models.SensorTimeBlock.period_id == models.Period.id)
            .filter(
            models.Period.user_id == user_id,
            models.SensorTimeBlock.time >= start,
            models.SensorTimeBlock.time <= end
            ).order_by(models.SensorTimeBlock.time).all())

    return [
        {
            "time": t.strftime("%H:%M:%S"),
            "iaq": prediction_data.iaq,
            "tvoc": prediction_data.tvoc,
            "eco2": prediction_data.eco2,
            "etoh": prediction_data.etoh
        }
        for t, prediction_data in rows
    ]


def get_all_metrics_formatted(user_id: int, target_date: date, db: Session):
    data = get_daily_data(user_id, target_date, db)
    return {
        "iaq": [{"time": item["time"], "value": item["iaq"]} for item in data if item["iaq"] is not None],
        "tvoc": [{"time": item["time"], "value": item["tvoc"]} for item in data if item["tvoc"] is not None],
        "eco2": [{"time": item["time"], "value": item["eco2"]} for item in data if item["eco2"] is not None],
        "etoh": [{"time": item["time"], "value": item["etoh"]} for item in data if item["etoh"] is not None]
    }


def clear_prediction_data(user_id: int, db: Session):
    """Xóa toàn bộ dữ liệu prediction của user"""
    # Lấy tất cả periods của user
    periods = db.query(models.Period).filter(
        models.Period.user_id == user_id
    ).all()

    deleted_count = 0

    for period in periods:
        # Lấy tất cả blocks của period
        blocks = db.query(models.SensorTimeBlock).filter(
            models.SensorTimeBlock.period_id == period.id
        ).all()

        for block in blocks:
            # Xóa prediction data
            deleted_count += db.query(models.PredictionData).filter(
                models.PredictionData.block_id == block.id
            ).delete()

            # Xóa block
            db.delete(block)

        # Xóa period
        db.delete(period)

    db.commit()
    return {"message": "Prediction data cleared successfully", "deleted_records": deleted_count}
