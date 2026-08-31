from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import Settings

settings = Settings()

engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
)
