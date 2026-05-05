from fastapi import FastAPI
from database import engine
from routers import sensors, predictions, user, authentication
from fastapi.middleware.cors import CORSMiddleware
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(authentication.router)
app.include_router(sensors.router)
app.include_router(predictions.router)
app.include_router(user.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://air-quality-dashboard-eta.vercel.app",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
