from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models.base import Base
from app.routes.pet_router import router as pet_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(pet_router)
