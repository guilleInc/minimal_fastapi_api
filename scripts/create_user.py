import asyncio
import os
from getpass import getpass

from app.database import SessionLocal, engine, settings
from app.domain.users import UserIn
from app.models.base import Base
from app.repositories.user_repository import SqlaUserRepository
from app.security.password_hasher import PasswordHasher
from app.services.user_service import UserService


async def ensure_database() -> None:
    if os.path.exists(settings.database_path):
        return

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def create_user(username: str, password: str) -> int:

    user_in = UserIn(username=username, password=password)

    async with SessionLocal() as session:
        service = UserService(
            session=session,
            user_repository=SqlaUserRepository(session=session),
            password_hasher=PasswordHasher(),
        )
        user = await service.add_user(user_in)

    return user.id


def get_password() -> str:
    password = getpass("Password: ")
    confirmation = getpass("Confirm password: ")

    if password != confirmation:
        raise ValueError("Passwords do not match")

    return password


async def main() -> None:
    await ensure_database()

    username = input("Username: ")
    password = get_password()

    try:
        user_id = await create_user(username, password)
    except Exception as e:
        raise SystemExit(str(e)) from e

    print(f"Created user '{username}' with ID {user_id}")


if __name__ == "__main__":
    asyncio.run(main())
