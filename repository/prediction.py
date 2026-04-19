from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import models

# 🔹 insert init 8640 mẫu


def insert_init(values: list[float], db: Session):
    today = datetime.utcnow().date()

    db.query(models.Prediction)\
        .filter(models.Prediction.date == today)\
        .filter(models.Prediction.type == "init")\
        .delete()

    data = [
        models.Prediction(
            date=today,
            step=i,
            value=val,
            type="init"
        )
        for i, val in enumerate(values)
    ]

    db.bulk_save_objects(data)
    db.commit()

    return {"status": "init data inserted"}


# 🔹 lấy init
def get_init(db: Session):
    today = datetime.utcnow().date()

    return db.query(models.Prediction)\
        .filter(models.Prediction.date == today)\
        .filter(models.Prediction.type == "init")\
        .order_by(models.Prediction.step)\
        .all()


# 🔹 insert realtime
def add_realtime(request, db: Session):
    today = datetime.utcnow().date()

    last_step = db.query(func.max(models.Prediction.step))\
        .filter(models.Prediction.date == today)\
        .filter(models.Prediction.type == "realtime")\
        .scalar()

    next_step = 0 if last_step is None else last_step + 1

    if next_step >= 8640:
        next_step = 0

    db.add(models.Prediction(
        date=today,
        step=next_step,
        value=request.value,
        type="realtime"
    ))

    db.commit()

    return {"status": "ok"}


# 🔹 lấy realtime
def get_realtime(limit: int, db: Session):
    today = datetime.utcnow().date()

    return db.query(models.Prediction)\
        .filter(models.Prediction.date == today)\
        .filter(models.Prediction.type == "realtime")\
        .order_by(models.Prediction.step.desc())\
        .limit(limit)\
        .all()
