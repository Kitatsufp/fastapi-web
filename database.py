import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Lấy biến môi trường
DATABASE_URL = os.getenv("DATABASE_URL")

# Nếu không có → fallback sang SQLite (để chạy local)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"
    print("⚠️ Using SQLite fallback")
else:
    print("✅ Using DATABASE_URL")

# Fix cho PostgreSQL trên Render
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg2://", 1
    )

# SQLite cần thêm connect_args
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
