from fastapi import APIRouter, status
from fastapi.responses import Response

from app.dependencies import PetServiceDep
from app.domain.pets import PetCreate, PetUpdate
from app.schemas.pet_schema import PetCreateSchema, PetSchema, PetUpdateSchema

router = APIRouter(
    prefix="/pets",
    tags=["pets"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request payload"},
        status.HTTP_404_NOT_FOUND: {"description": "Pet not found"},
    },
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_pet(payload: PetCreateSchema, service: PetServiceDep) -> PetSchema:
    domain_pet = PetCreate.model_validate(payload.model_dump())
    return PetSchema.model_validate(await service.add_pet(domain_pet))


@router.get("/")
async def list_pets(service: PetServiceDep) -> list[PetSchema]:
    return [PetSchema.model_validate(pet) for pet in await service.get_pets()]


@router.get("/{pet_id}")
async def get_pet(pet_id: int, service: PetServiceDep) -> PetSchema:
    return PetSchema.model_validate(await service.get_pet(pet_id))


@router.patch("/{pet_id}")
async def update_pet(pet_id: int, payload: PetUpdateSchema, service: PetServiceDep) -> PetSchema:
    domain_update = PetUpdate.model_validate(payload.model_dump(exclude_unset=True))
    return PetSchema.model_validate(await service.update_pet(pet_id, domain_update))


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet(pet_id: int, service: PetServiceDep) -> None:
    await service.delete_pet(pet_id)


@router.options("/", include_in_schema=False)
async def options_pets() -> Response:
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"Allow": "GET, POST, OPTIONS"},
    )


@router.options("/{pet_id}", include_in_schema=False)
async def options_pet_item() -> Response:
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"Allow": "DELETE, GET, PATCH, OPTIONS"},
    )
