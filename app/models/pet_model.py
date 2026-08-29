from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PetModel(Base):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    species: Mapped[str] = mapped_column(String(50))
    breed: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(100))
    owner_name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
