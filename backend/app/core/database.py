from collections.abc import Generator

from fastapi import HTTPException, status
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = None
SessionLocal = None

if settings.database_url:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库未配置，请在 .env 中设置 DATABASE_URL",
        )

    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库访问失败：{exc}",
        ) from exc
    finally:
        db.close()


def check_database_connection() -> tuple[bool, str]:
    if engine is None:
        return False, "数据库未配置，请在 .env 中设置 DATABASE_URL"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "数据库连接正常"
    except SQLAlchemyError as exc:
        return False, f"数据库连接失败：{exc}"
