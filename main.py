from fastapi import FastAPI
from database import engine
from routers import blog, user, authentication, prediction
from fastapi.middleware.cors import CORSMiddleware
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(authentication.router)
app.include_router(blog.router)
app.include_router(user.router)
app.include_router(prediction.router)

# CORS Configuration - Allow Vercel frontend and local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://air-quality-dashboard-eta.vercel.app",  # Production Vercel URL
        "http://localhost:3000",                          # Local React dev
        "http://localhost:8080",                          # Local HTML testing
        "http://127.0.0.1:3000",                          # Alternative localhost
        "http://127.0.0.1:8080",                          # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
