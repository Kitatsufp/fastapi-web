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
        iaq_raw=request.iaq_raw,
        tvoc_raw=request.tvoc_raw,
        eco2_raw=request.eco2_raw,
        etoh_raw=request.etoh_raw,
        block_id=block.id
    )
    db.add(prediction_data)
    db.commit()
    db.refresh(prediction_data)

    # ✅ Trả về dict thay vì object SQLAlchemy để tránh lỗi lazy loading
    return {
        "time": now,
        "period": period_name,
        "block": block_name,
        "iaq": prediction_data.iaq,
        "tvoc": prediction_data.tvoc,
        "eco2": prediction_data.eco2,
        "etoh": prediction_data.etoh,
        "iaq_raw": prediction_data.iaq_raw,
        "tvoc_raw": prediction_data.tvoc_raw,
        "eco2_raw": prediction_data.eco2_raw,
        "etoh_raw": prediction_data.etoh_raw,
    }


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
            "etoh": prediction_data.etoh,
            "iaq_raw": prediction_data.iaq_raw,
            "tvoc_raw": prediction_data.tvoc_raw,
            "eco2_raw": prediction_data.eco2_raw,
            "etoh_raw": prediction_data.etoh_raw
        }
        for t, prediction_data in rows
    ]


def get_all_metrics_formatted(user_id: int, target_date: date, db: Session):
    data = get_daily_data(user_id, target_date, db)
    return {
        "iaq": [{"time": item["time"], "value": item["iaq"]} for item in data if item["iaq"] is not None],
        "tvoc": [{"time": item["time"], "value": item["tvoc"]} for item in data if item["tvoc"] is not None],
        "eco2": [{"time": item["time"], "value": item["eco2"]} for item in data if item["eco2"] is not None],
        "etoh": [{"time": item["time"], "value": item["etoh"]} for item in data if item["etoh"] is not None],
        "iaq_raw": [{"time": item["time"], "value": item["iaq_raw"]} for item in data if item["iaq_raw"] is not None],
        "tvoc_raw": [{"time": item["time"], "value": item["tvoc_raw"]} for item in data if item["tvoc_raw"] is not None],
        "eco2_raw": [{"time": item["time"], "value": item["eco2_raw"]} for item in data if item["eco2_raw"] is not None],
        "etoh_raw": [{"time": item["time"], "value": item["etoh_raw"]} for item in data if item["etoh_raw"] is not None]
    }
