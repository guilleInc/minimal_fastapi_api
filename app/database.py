from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./pets.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, autoflush=False, autocommit=False, expire_on_commit=False)
