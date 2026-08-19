from fastapi import APIRouter, status

from app.dependencies import PetServiceDep
from app.schemas.pet_schema import PetCreateSchema, PetSchema, PetUpdateSchema

router = APIRouter(prefix="/pets", tags=["pets"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_pet(payload: PetCreateSchema, service: PetServiceDep) -> PetSchema:
    return await service.add_pet(payload)


@router.get("/")
async def list_pets(service: PetServiceDep) -> list[PetSchema]:
    return await service.get_pets()


@router.get("/{pet_id}")
async def get_pet(pet_id: int, service: PetServiceDep) -> PetSchema:
    return await service.get_pet(pet_id)


@router.put("/{pet_id}")
async def update_pet(pet_id: int, payload: PetUpdateSchema, service: PetServiceDep) -> PetSchema:
    return await service.update_pet(pet_id, payload)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet(pet_id: int, service: PetServiceDep) -> None:
    await service.delete_pet(pet_id)
