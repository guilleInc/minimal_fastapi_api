from fastapi import APIRouter, HTTPException, status

from app.dependencies import PetServiceDep
from app.schemas.pet_schema import PetCreate, Pet, PetUpdate

router = APIRouter(prefix="/pets", tags=["pets"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_pet(payload: PetCreate, service: PetServiceDep) -> Pet:
    return await service.add_pet(payload)


@router.get("/")
async def list_pets(service: PetServiceDep) -> list[Pet]:
    return await service.get_pets()


@router.get("/{pet_id}")
async def get_pet(pet_id: int, service: PetServiceDep) -> Pet:
    try:
        return await service.get_pet(pet_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{pet_id}")
async def update_pet(pet_id: int, payload: PetUpdate, service: PetServiceDep) -> Pet:
    try:
        return await service.update_pet(pet_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet(pet_id: int, service: PetServiceDep) -> None:
    try:
        await service.delete_pet(pet_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
