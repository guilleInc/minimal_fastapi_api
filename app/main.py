from fastapi import FastAPI

from app.database import engine
from app.models.pet_model import Base
from app.routes.pet_router import router as pet_router

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(pet_router)
