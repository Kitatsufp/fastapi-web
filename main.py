from fastapi import FastAPI
from database import engine
from routers import blog, user, authentication
from fastapi.middleware.cors import CORSMiddleware
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(authentication.router)
app.include_router(blog.router)
app.include_router(user.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://air-quality-dashboard-eta.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
